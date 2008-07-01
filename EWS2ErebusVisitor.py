from CNodeVisitor import *
from CNode import *
from namespaces import *
from helper.id import identity
from helper.timeconv import *
from helper.icalconv import *
from hashlib import sha1

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

    def __gen_id(self,tz):
        s = str(tz)
        return sha1(s).hexdigest()

    def add_tz(self,tz):
        """Add a timezone element.

        Return the corresponding tzid (sha1 sum of the actual content)
        """
        tzid = CNode(name='tzid', content=self.__gen_id(tz))
        tz.add_child(tzid)

        old = None
        for t in self.timezones.children:
            if tzid.content == t.search('tzid').content:
                old = t

        if not old:
            self.timezones.add_child(tz)

        return tzid.content

    def visit_start(self):
        for eci in self.ews_calendaritems:
            ci = self.visit(eci)
            self.events.add_child(ci)

        return self.calendar

    def visitCalendarItem(self,eci):
        ci = CNode(name='event')

        def conv(ews, att, f):
            ews_e = eci.search(ews)
            if not ews_e: return
            new = f(ews_e.content)
            if not new: return

            ci.attr[att] = new

        rec = self.accept1(eci, 'Recurrence')
        if rec: ci.add_child(rec)

        tz = self.accept1(eci, 'MeetingTimeZone')
        if tz:
            tzid = self.add_tz(tz)
            ci.add_child(CNode(name='tzid',content=tzid))
        
        conv('Subject', 'summary', identity)
        conv('Start', 'start', xsdt2datetime)
        conv('End', 'end', xsdt2datetime)
        conv('Sensitivity', 'class', sensitivity2class)
        conv('Location', 'location', identity)
        conv('DateTimeCreated', 'timestamp', xsdt2datetime)
        conv('Body', 'description', identity)

        return ci

    def visit_any(self,eci):
        """Copy the entire tree from here"""
        ci = CNode(name=eci.name)
        ci.content = eci.content

        for c in eci.children:
            ci.add_child(self.visit(c))

        return ci


