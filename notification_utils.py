import json
import logging
from datetime import datetime, timedelta, tzinfo

from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.api.taskqueue import TaskRetryOptions
from google.appengine.ext import deferred
from twilio.rest import TwilioRestClient
import pytz

import utils
from pytz import timezone
from models import Notification


def get_parent_key_email_from_notification(notification):
    return notification.key.parent().string_id()


def delete_notification(notification):
    if notification.is_in_task_queue:
        task_name = notification.get_task_name()
        taskqueue.Queue().delete_tasks_by_name(task_name)  # Removes the scheduled task event
    notification.key.delete();


# Different queries to get TextMessageEvents for this user.
def get_all_notifications_for_user(user):
    """ Gets all of the contacts for this user. """
    parent_key = utils.get_parent_key(user)
    return Notification.query(ancestor=parent_key)


def get_unsent_notifications_for_user(user):
    query = get_all_notifications_for_user(user).order(-Notification.time)  # Closest to now on top
    return query.filter(Notification.type != 2).fetch()


def get_sent_notifications_for_user(user, limit=20):
    query = get_all_notifications_for_user(user).order(-Notification.time)  # Closest to now on top
    return query.filter(Notification.type == 2).fetch(limit)


def send_notification(notification):
    # Get the Twilio account information needed to send this text message event.
    creators_email = str(notification.creator)
    route = notification.key.parent().get()
    route_name = route.name
    body = "Don't forget to check your route " + route_name + " on Travel Companion! Find it at " + "www.travel-companion.me/?route=" + route.key.urlsafe()

    account_sid = "AC56dcdc34222550e22aa248491d16af63"
    auth_token = "32718999e68e03a0b87e4e5787c29e7c"
    from_number = "+18126457333"

    client = TwilioRestClient(account_sid, auth_token)

    # Send the message only to the appropriate contacts.
    if not '@' in notification.receiver:
        to_number = "+1" + str(notification.receiver)
        # Twilio library code:  https://github.com/twilio/twilio-python
        # Twilio library docs: http://twilio-python.readthedocs.io/en/latest/
        rv = client.messages.create(to=to_number,
                                    from_=from_number,
                                    body=body)
        if rv.error_message:
            logging.info("Message had an error " + rv.error_message)
    else:
        try:
            message = mail.EmailMessage(
                sender="email_service@travel-companion-146516.appspotmail.com",
                subject="Message From Travel Companion! Your Personal Travel Companion!")
            message.to = notification.receiver
            message.body = body
            message.send()
        except Exception as err:
            logging.error("The email did not send! Avoid the retry " + err.message)
        else:
            raise Exception("Invalid Message Type")

    if notification.type == 0:
        notification.type = 2
        notification.put()


def send_notification_now(notification):
    notification.type = 2
    notification.put()
    deferred.defer(send_notification_for_event_key, notification.key)


def send_notification_for_event_key(notification_key):
    notification = notification_key.get()
    #try:
    send_notification(notification)
    #except:
    #    logging.error("Sending the message failed. Catching the error to avoid the retry.")


def add_notification_to_task_queue(notification):
    if notification.is_in_task_queue:
        return

    notification.is_in_task_queue = True
    notification_key = notification.put()  # Also done to get the key to use as the name of the task.

    # https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.taskqueue#google.appengine.api.taskqueue.add
    payload = {"urlsafe_entity_key": notification_key.urlsafe()}
    eta = datetime.now(timezone('US/Eastern'))
    if eta.hour < notification.time.hour:
        etaDay = eta.day
        etaMonth = eta.month
        etaYear = eta.year
    elif eta.hour == notification.time.hour:
        if eta.minute < notification.time.minute:
            etaDay = eta.day
            etaMonth = eta.month
            etaYear = eta.year
        else:
            tomorrow = eta + timedelta(days=1)
            etaDay = tomorrow.day
            etaMonth = tomorrow.month
            etaYear = tomorrow.year
    else:
        tomorrow = eta + timedelta(days=1)
        etaDay = tomorrow.day
        etaMonth = tomorrow.month
        etaYear = tomorrow.year
    eta = eta.replace(second=0, hour=notification.time.hour, minute=notification.time.minute, day=etaDay,
                      month=etaMonth,
                      year=etaYear)
    notification.time = notification.time.replace(day=eta.day, month=eta.month, year=eta.year)
    notification.put()
    taskqueue.add(url='/queue/send-notification',
                  name=notification.get_task_name() + eta.strftime("%m%d%Y%I%M"),
                  payload=json.dumps(payload),
                  eta=eta,
                  retry_options=TaskRetryOptions(task_retry_limit=1))
