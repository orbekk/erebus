from CNodeVisitor import *
from CNode import *
from helper.id import identity
from helper.timeconv import *
from helper.icalconv import *
from helper.recurrence import *
from hashlib import sha1

class ToLowerCaseVisitor(CNodeVisitor):
    def visit_any(self, o):
        o.name = o.name.lower()
        new_attr = {}
        for k,v in o.attr.iteritems():
            new_attr[k.lower()] = v
        o.attr = new_attr
        
        [self.visit(c) for c in o.children]

class ICS2ErebusVisitor(CNodeVisitor):

    def __init__(self,cnode):
        self.calendar = CNode(name='calendar')
        self.timezones = CNode(name='timezones')
        self.timezone_ids = {}
        self.events = CNode(name='events')

        self.calendar.add_child(self.timezones)
        self.calendar.add_child(self.events)

        ToLowerCaseVisitor().visit(cnode)
        self.ics = cnode

    def visit_start(self):
        timezones = self.accept(self.ics, 'vtimezone')
        events = self.accept(self.ics, 'vevent')

        for e in timezones:
            self.timezones.add_child(e)
        for e in events:
            self.events.add_child(e)

        return self.calendar

    def visit_vtimezone(self,ics):
        tz = CNode(name='timezone')
        
        #         if freq == 'YEARLY':
        #             recpattern = rrule2yearly_recpattern(rrule, interval_e, self.get('t:Start'))
        #             recurrence.append(recpattern)
        return tz

    def visit_vevent(self,ics):
        event = CNode(name='event')

        def conv(icaln, ebus, f):

            if not ics.attr.has_key(icaln): return
            ics_e = ics.attr[icaln]
            if not ics_e: return
            new = f(ics_e)
            if not new: return

            event.attr[ebus] = new
            
        conv('summary', 'summary', identity)
        conv('dtstart', 'start', vDDD2dt)
        conv('dtend', 'end', vDDD2dt)
        conv('class', 'class', identity)
        conv('location', 'location', identity)
        conv('dtstamp', 'timestamp', vDDD2dt)
        conv('description', 'description', identity)

        if ics.attr.has_key('rrule'):
            rec = rrule2recurrence(ics.attr['rrule'], event.attr['start'])
            if rec: event.add_child(rec)

        return event
