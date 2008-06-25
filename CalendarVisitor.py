from Calendar import *
from CalendarItem import *
from Recurrence import *
from TimeZone import *

class CalendarVisitor(object):
    def visit(self,obj):
        method = getattr(self, "visit%s" % obj.__class__.__name__)
        if method:
            return method(obj)
        else:
            raise MissingVisitor("visit%s" % obj.__class__.__name__)

    def accept(self,obj,attr):
        """Call this to visit a child with name 'attr'"""
        return [self.visit(o) for o in getattr(obj, attr)]
