from Calendar import *
from CalendarItem import *
from Recurrence import *
from TimeZone import *

class CalendarVisitor(object):
    def accept(self,obj,attr):
        """Call this to visit a child with name 'attr'"""
        return [o.accept(self) for o in getattr(obj, attr)]
