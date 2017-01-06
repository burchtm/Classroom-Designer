from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from protorpc.messages import Enum

#TODO UPDATE!
class Route(ndb.Model):
    """
         The Route Entity will be the essential starting place for the web app.
         The Route will belong to a user and will have different types inclucing:
         Recent, Saved, Both Recent and Saved, as well as Daily or Not
    """
    created_by = ndb.StringProperty()
    name = ndb.StringProperty()
    type = ndb.IntegerProperty()
    daily = ndb.IntegerProperty()
    start_time = ndb.DateTimeProperty()
    last_touch_date_time = ndb.DateTimeProperty(auto_now=True)

class Stop(ndb.Model):
    """
        The Stop Entity will be a destination, belonging to a Route Entity.
    """
    route_key = ndb.KeyProperty(kind=Route)
    order_number = ndb.IntegerProperty()
    stop_name = ndb.StringProperty()
    ordered = ndb.BooleanProperty()
#     streetOne = ndb.StringProperty()
#     streetTwo = ndb.StringProperty()
#     city = ndb.StringProperty()
#     state = ndb.StringProperty()
#     zip = ndb.StringProperty()

class Notification(ndb.Model):
    """
        The Notification Entity will be used to send messages between two users
    """
    creator = ndb.StringProperty()
    receiver = ndb.StringProperty()
    time = ndb.DateTimeProperty()
    type = ndb.IntegerProperty()
    message = ndb.StringProperty()
    is_in_task_queue = ndb.BooleanProperty(default=False)
    def get_task_name(self):
        """ Returns a unique name for this text message event."""
        return self.key.urlsafe()  # Just use the entity key urlsafe string (ugly for display but easy)
