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
        """Call this to visit children with name 'attr'"""
        return [self.visit(o) for o in getattr(obj, attr)]

    def accept1(self,obj,attr):
        """Call this to visit the first child with name 'attr'"""
        its = getattr(obj, attr)
        if len(its) > 0:
            self.visit(its[0])
        else:
            return None
