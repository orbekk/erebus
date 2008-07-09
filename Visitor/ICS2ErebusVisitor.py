# -*- coding: utf-8 -*-
from Visitor.CNodeVisitor import *
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

    def run(self):
        timezones = self.accept(self.ics, 'vtimezone')
        events = self.accept(self.ics, 'vevent')

        for e in timezones:
            self.timezones.add_child(e)
        for e in events:
            self.events.add_child(e)

        return self.calendar

    def __convert_timezone(self,ics):

        if ics.name == 'standard':
            tz_e = CNode(name='Standard')
        elif ics.name == 'daylight':
            tz_e = CNode(name='Daylight')
        else:
            raise ValueError("Unknown timezone type: %s", ics.name)

        offset = utcoffset2vDDD(ics.attr['tzoffsetto'], negate=True)
        offset_e = CNode(name='Offset',content=offset)
        tz_e.add_child(offset_e)

        rrule = ics.attr['rrule']
        start = ics.attr['dtstart']
        if rrule:
            rec = rrule2recurrence(rrule, start)
            tz_e.add_child(rec.children[0])

        time = start.dt
        timestr = "%.2d:%.2d:%.2d" %(time.hour, time.minute, time.second)
        time_e = CNode(name='Time',content=timestr)

        tz_e.add_child(time_e)

        return tz_e

    def visit_vtimezone(self,ics):
        tz = CNode(name='TimeZone')

        baseoffset_e = CNode(name='BaseOffset',content='PT0M')
        tz.add_child(baseoffset_e)

        if len(ics.children) == 1:
            # Just add a base offset
            std_e = ics.children[0]
            # TODO: fix this
        else:
            tz_s = self.__convert_timezone(ics.search('standard'))
            tz.add_child(tz_s)
            tz_d = self.__convert_timezone(ics.search('daylight'))
            tz.add_child(tz_d)

        tzid = gen_tz_id(tz)
        tzid_e = CNode(name='tzid',content=tzid)
        tz.add_child(tzid_e)
        
        self.timezone_ids[ics.attr['tzid']] = tzid

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
            if rec:
                event.add_child(rec)
                rec_range = rrule2range(ics.attr['rrule'], event.attr['start'])
                rec.add_child(rec_range)

        if ics.attr['dtstart'].params.has_key('tzid'):
            i_tzid = ics.attr['dtstart'].params['tzid']
            tz = self.timezone_ids[i_tzid]
            tz_e = CNode(name='tzid',content=tz)
            event.add_child(tz_e)

        return event
