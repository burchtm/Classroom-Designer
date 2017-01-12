from google.appengine.ext import ndb

class ClassList(ndb.Model):
    """
         The ClassList Entity will be the the different class lists imported by each teacher.
    """
    created_by = ndb.StringProperty()
    name = ndb.StringProperty()
    last_touch_date_time = ndb.DateTimeProperty(auto_now=True)


class Student(ndb.Model):
    """
        The Student Entity will be a student in a ClassList Entity.
    """
    classList_key = ndb.KeyProperty(kind=ClassList)
    name = ndb.StringProperty()


class Floorplan(ndb.Model):
    """
        The Floorplan Entity will be used to model each floorplan
    """
    classList_key = ndb.KeyProperty(kind=ClassList)
    name = ndb.StringProperty()


class Desk(ndb.Model):
    """
        The Desk Entity will be used to model each desk and its location
    """
    student_key = ndb.KeyProperty(kind=Student)
    floorplan_key = ndb.KeyProperty(kind=Floorplan)
    location = ndb.GeoPtProperty()
