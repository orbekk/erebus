from CNodeVisitor import *
from CNode import *
from helper.id import identity
from helper.timeconv import *
from helper.icalconv import *
from hashlib import sha1

class ICS2ErebusVisitor(CNodeVisitor):

    def __init__(self,cnode):
        self.calendar = CNode(name='calendar')
        self.timezones = CNode(name='timezones')
        self.timezone_ids = {}
        self.events = CNode(name='events')

        self.calendar.add_child(self.timezones)
        self.calendar.add_child(self.events)
        
        self.ics = cnode

    def visit_start(self):
        timezones = self.accept(self.ics, 'VTIMEZONE')
        events = self.accept(self.ics, 'VEVENT')

        for e in timezones:
            self.timezones.add_child(e)
        for e in events:
            self.events.add_child(e)

        return self.calendar

    def visitVTIMEZONE(self,ics):
        tz = CNode(name='timezone')
        print "i has it"
        
        #         if freq == 'YEARLY':
        #             recpattern = rrule2yearly_recpattern(rrule, interval_e, self.get('t:Start'))
        #             recurrence.append(recpattern)
        return tz

    def visitVEVENT(self,ics):
        event = CNode(name='event')

        def conv(icaln, ebus, f):
            if not ics.attr.has_key(icaln): return
            ics_e = ics.attr[icaln]
            if not ics_e: return
            new = f(ics_e)
            if not new: return

            event.attr[ebus] = new
            
        conv('summary', 'summary', identity)
        conv('dtstart', 'start', identity)

        return event
