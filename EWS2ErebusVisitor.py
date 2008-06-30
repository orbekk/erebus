from CNodeVisitor import *
from CNode import *
from namespaces import *
from helper.id import identity
from helper.timeconv import *
from helper.icalconv import *

class StripNamespaceVisitor(CNodeVisitor):
    def visit_any(self, o):
        o.name = no_namespace(o.name)
        [self.visit(c) for c in o.children]

class EWS2ErebusVisitor(CNodeVisitor):

    def __init__(self,cnode):
        self.calendar = CNode(name='calendar')
        self.timezones = CNode(name='timezones')
        self.events = CNode(name='events')

        self.calendar.add_child(self.timezones)
        self.calendar.add_child(self.events)
        
        # Strip namespace from cnode
        StripNamespaceVisitor().visit(cnode)

        self.ews_calendaritems = []
        
        for item in cnode.search('CalendarItem',all=True,keep_depth=True):
            self.ews_calendaritems.append(item)

    def visit_start(self):
        [self.visit(ci) for ci in self.ews_calendaritems]

        return self.calendar

    def visitCalendarItem(self,eci):
        ci = CNode(name='event')

        def conv(ews, att, f):
            ews_e = eci.search(ews)
            if not ews_e: return
            new = f(ews_e.content)
            if not new: return

            ci.attr[att] = new

        conv('Subject', 'summary', identity)
        conv('Start', 'start', xsdt2datetime)
        conv('End', 'end', xsdt2datetime)
        conv('Sensitivity', 'class', sensitivity2class)
        conv('Location', 'location', identity)
        conv('DateTimeCreated', 'timestamp', xsdt2datetime)
        conv('Body', 'description', identity)

        self.events.add_child(ci)
