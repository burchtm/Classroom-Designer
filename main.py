import json
import logging
from datetime import date
import datetime
import email
import os

from google.appengine.api import users
from google.appengine.api.taskqueue import taskqueue
from google.appengine.ext import ndb
import jinja2
import webapp2

import notification_utils
from handlers import base_handlers
from models import Route, Notification, Stop
import utils


# Jinja environment instance necessary to use Jinja templates.
def __init_jinja_env():
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols", "jinja2.ext.with_"],
        autoescape=True)
    # Example of a Jinja filter (useful for formatting data sometimes)
    #   jenv.filters["time_and_date_format"] = date_utils.time_and_date_format
    return jenv


jinja_env = __init_jinja_env()


class MainHandler(base_handlers.BasePage):
    def update_values(self, values):
        pass

    def get_template(self):
        return jinja_env.get_template("templates/base_page.html")


class HomeHandler(base_handlers.BasePage):
    def update_values(self, values):
        values["user_email"] = users.get_current_user().email().lower()
        url_route_key = self.request.get('route')
        if url_route_key != "":
            route_key = ndb.Key(urlsafe=url_route_key)
            # Next two lines are so that the recent routes list populates correctly.
            route = route_key.get()
            route.put()
            stops_query = Stop.query(ancestor=route_key).order(Stop.order_number).fetch()
            stop1 = stops_query[0]
            values["stop1"] = stop1.stop_name
            if stop1.ordered:
                values["stop1_checkbox"] = "on"
            else:
                values["stop1_checkbox"] = "off"
            if (len(stops_query) > 1):
                stop2 = stops_query[1]
                values["stop2"] = stop2.stop_name
                if stop2.ordered:
                    values["stop2_checkbox"] = "on"
                else:
                    values["stop2_checkbox"] = "off"
            if (len(stops_query) > 2):
                stop3 = stops_query[2]
                values["stop3"] = stop3.stop_name
                if stop3.ordered:
                    values["stop3_checkbox"] = "on"
                else:
                    values["stop3_checkbox"] = "off"
            if (len(stops_query) > 3):
                stop4 = stops_query[3]
                values["stop4"] = stop4.stop_name
                if stop4.ordered:
                    values["stop4_checkbox"] = "on"
                else:
                    values["stop4_checkbox"] = "off"
            if (len(stops_query) > 4):
                stop5 = stops_query[4]
                values["stop5"] = stop5.stop_name
                if stop5.ordered:
                    values["stop5_checkbox"] = "on"
                else:
                    values["stop5_checkbox"] = "off"
            values["entity_key"] = url_route_key
        else:
            route_key = ""
        recent_routes_query = Route.query(
            ancestor=utils.get_parent_key_for_email(users.get_current_user().email())).order(
            -Route.last_touch_date_time)
        values["recent_routes"] = recent_routes_query.fetch(5)
        my_routes_query = Route.query(ancestor=utils.get_parent_key_for_email(users.get_current_user().email())).filter(
            Route.type == 1).order(Route.name)
        values["my_routes"] = my_routes_query.fetch()
        my_notifications_query = Notification.query(
            ancestor=utils.get_parent_key_for_email(users.get_current_user().email())).filter(
            Notification.type != 2)
        values["my_notifications"] = my_notifications_query.fetch()

    def get_template(self):
        return jinja_env.get_template("templates/home.html")


class LoginPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        template = jinja_env.get_template("templates/login.html")
        values = {"login_url": users.create_login_url("/")}
        self.response.out.write(template.render(values))


class CreateRouteAction(webapp2.RequestHandler):
    def post(self):
        if self.request.get('edit-route-entity-key'):
            route_key = ndb.Key(urlsafe=str(self.request.get('edit-route-entity-key')))
            new_route = route_key.get()
            routeStops = Stop.query(ancestor=route_key).order(Stop.order_number).fetch()

            dictionary = {}
            Stop1 = self.request.get('stop1')
            if self.request.get('stop1-checkbox') == 'on':
                Checkbox1 = True
            else:
                Checkbox1 = False
            dictionary["Stop1"] = Stop1
            dictionary["Checkbox-Stop1"] = Checkbox1
            lastStop = self.request.get('stop2')
            Stop2 = lastStop
            if self.request.get('stop2-checkbox') == 'on':
                Checkbox2 = True
            else:
                Checkbox2 = False
            dictionary["Stop2"] = Stop2
            dictionary["Checkbox-Stop2"] = Checkbox2
            Stop3 = ""
            Stop4 = ""
            Stop5 = ""

            if self.request.get('stop3'):
                lastStop = self.request.get('stop3')
                Stop3 = lastStop
                if self.request.get('stop3-checkbox') == 'on':
                    Checkbox3 = True
                else:
                    Checkbox3 = False
                dictionary["Stop3"] = Stop3
                dictionary["Checkbox-Stop3"] = Checkbox3

            if self.request.get('stop4'):
                lastStop = self.request.get('stop4')
                Stop4 = lastStop
                if self.request.get('stop4-checkbox') == 'on':
                    Checkbox4 = True
                else:
                    Checkbox4 = False
                dictionary["Stop4"] = Stop4
                dictionary["Checkbox-Stop4"] = Checkbox4

            if self.request.get('stop5'):
                lastStop = self.request.get('stop5')
                Stop5 = lastStop
                if self.request.get('stop5-checkbox') == 'on':
                    Checkbox5 = True
                else:
                    Checkbox5 = False
                dictionary["Stop5"] = Stop5
                dictionary["Checkbox-Stop5"] = Checkbox5

            new_route.name = Stop1 + " to " + lastStop

            for i in range(1, (len(dictionary.keys()) / 2) + 1):
                if i < len(routeStops) + 1:
                    routeStops[i - 1].ordered = dictionary["Checkbox-Stop" + str(i)]
                    routeStops[i - 1].stop_name = dictionary["Stop" + str(i)]
                    routeStops[i - 1].put()
                else:
                    new_stop = Stop(parent=new_route.key,
                                    route_key=new_route.key,
                                    order_number=i,
                                    stop_name=dictionary["Stop" + str(i)],
                                    ordered=dictionary["Checkbox-Stop" + str(i)])
                    new_stop.put()

            new_route.put()
        else:
            firstStop = self.request.get('stop1')
            if self.request.get('stop1-checkbox') == 'on':
                firstCheckbox = True
            else:
                firstCheckbox = False
            lastStop = self.request.get('stop2')
            secondStop = lastStop
            if self.request.get('stop2-checkbox') == 'on':
                secondCheckbox = True
            else:
                secondCheckbox = False
            thirdStop = ""
            fourthStop = ""
            fifthStop = ""

            if self.request.get('stop3'):
                lastStop = self.request.get('stop3')
                thirdStop = lastStop
                if self.request.get('stop3-checkbox') == 'on':
                    thirdCheckbox = True
                else:
                    thirdCheckbox = False
            if self.request.get('stop4'):
                lastStop = self.request.get('stop4')
                fourthStop = lastStop
                if self.request.get('stop4-checkbox') == 'on':
                    fourthCheckbox = True
                else:
                    fourthCheckbox = False

            if self.request.get('stop5'):
                lastStop = self.request.get('stop5')
                fifthStop = lastStop
                if self.request.get('stop5-checkbox') == 'on':
                    fifthCheckbox = True
                else:
                    fifthCheckbox = False

            user = users.get_current_user()
            email = user.email().lower()
            # TODO: Name will change when modal has dynamic number of routes
            # NOTE: Created routes start with type = 0 (not saved)
            # NOTE: Created routes start with daily = 0 (non-recurring)
            new_route = Route(parent=utils.get_parent_key_for_email(email),
                              created_by=email,
                              name=firstStop + " to " + lastStop,
                              type=0,
                              daily=0,
                              start_time=datetime.datetime.now())
            new_route.put()

            new_stop1 = Stop(parent=new_route.key,
                             route_key=new_route.key,
                             order_number=1,
                             stop_name=self.request.get('stop1'),
                             ordered=firstCheckbox)
            new_stop1.put()
            new_stop2 = Stop(parent=new_route.key,
                             route_key=new_route.key,
                             order_number=2,
                             stop_name=self.request.get('stop2'),
                             ordered=secondCheckbox)
            new_stop2.put()
            if thirdStop != "":
                new_stop3 = Stop(parent=new_route.key,
                                 route_key=new_route.key,
                                 order_number=3,
                                 stop_name=self.request.get('stop3'),
                                 ordered=thirdCheckbox)
                new_stop3.put()
            if fourthStop != "":
                new_stop4 = Stop(parent=new_route.key,
                                 route_key=new_route.key,
                                 order_number=4,
                                 stop_name=self.request.get('stop4'),
                                 ordered=fourthCheckbox)
                new_stop4.put()
            if fifthStop != "":
                new_stop5 = Stop(parent=new_route.key,
                                 route_key=new_route.key,
                                 order_number=5,
                                 stop_name=self.request.get('stop5'),
                                 ordered=fifthCheckbox)
                new_stop5.put()

        self.redirect('/'.join(self.request.referer.split("/")[:3]) + "?route=" + str(new_route.key.urlsafe()))


class SaveRouteAction(webapp2.RequestHandler):
    def post(self):
        if self.request.get('save_entity_key'):
            route_key = ndb.Key(urlsafe=self.request.get('save_entity_key'))
            route = route_key.get()
            route.name = self.request.get('save-route-name')
            route.type = 1
            route.start_time = datetime.datetime.strptime(str(self.request.get('route-time')),
                                                          '%I:%M %p')
            route.put()
            self.redirect('/'.join(self.request.referer.split("/")[:3]) + "?route=" + str(route.key.urlsafe()))
        else:
            self.redirect('/')


class DeleteRouteAction(webapp2.RequestHandler):
    def get(self):
        current = self.request.get("current")
        to_delete = self.request.get("key")
        to_delete_key = ndb.Key(urlsafe=to_delete)
        to_delete_key.delete()
        if current == to_delete:
            self.redirect('/')
        else:
            self.redirect('/'.join(self.request.referer.split("/")[:3]) + "?route=" + str(current))


class CreateNotificationAction(webapp2.RequestHandler):
    def post(self):
        if self.request.get('notification-route-entity-key'):
            user = users.get_current_user()
            email = user.email().lower()
            receiver = self.request.get('notification-contact')
            if str(self.request.get('daily-notification')) == "on":
                notification_type = 1
            else:
                notification_type = 0
            route_key = ndb.Key(urlsafe=str(self.request.get('notification-route-entity-key')))
            route = route_key.get()
            route_time = route.start_time
            notification_time = route_time - datetime.timedelta(
                hours=int(self.request.get("notification-hour"))) - datetime.timedelta(
                minutes=int(self.request.get("notification-minute")))

            new_notification = Notification(parent=route_key,
                                            creator=email,
                                            receiver=receiver,
                                            time=notification_time,
                                            type=notification_type,
                                            message="")
            new_notification.put()
            notification_utils.add_notification_to_task_queue(new_notification)

            self.redirect('/'.join(self.request.referer.split("/")[:3]) + "?route=" + str(route.key.urlsafe()))
        else:
            self.redirect('/')


class DeleteNotificationAction(webapp2.RequestHandler):
    def get(self):
        current = self.request.get("current")
        to_delete = self.request.get("key")
        to_delete_key = ndb.Key(urlsafe=to_delete)
        being_deleted = to_delete_key.get()
        taskqueue.Queue().delete_tasks_by_name(
            being_deleted.get_task_name() + being_deleted.time.strftime("%m%d%Y%I%M"))
        to_delete_key.delete()
        self.redirect('/'.join(self.request.referer.split("/")[:3]) + "?route=" + str(current))


class QueueSendNotification(webapp2.RequestHandler):
    def post(self):
        payload = json.loads(self.request.body)
        urlsafe_entity_key = payload["urlsafe_entity_key"]
        notification_key = ndb.Key(urlsafe=urlsafe_entity_key)
        notification_utils.send_notification_for_event_key(notification_key)
        notification = notification_key.get()
        notification.is_in_task_queue = False
        notification.put()
        taskqueue.Queue().delete_tasks_by_name(notification.get_task_name())
        if notification.type == 0:
            notification.type = 2
            notification.put()
        else:
            notification_utils.add_notification_to_task_queue(notification)


app = webapp2.WSGIApplication([
    ('/login', LoginPage),
    ('/', HomeHandler),
    ('/edit-route', CreateRouteAction),
    ('/save', SaveRouteAction),
    ('/delete-route', DeleteRouteAction),
    ('/delete-notification', DeleteNotificationAction),
    ('/create-notification', CreateNotificationAction),
    ("/queue/send-notification", QueueSendNotification),

], debug=True)
