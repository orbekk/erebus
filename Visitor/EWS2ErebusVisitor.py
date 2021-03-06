# -*- coding: utf-8 -*-
from Visitor.CNodeVisitor import *
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

    def add_tz(self,tz):
        """Add a timezone element.

        Return the corresponding tzid (sha1 sum of the actual content)
        """
        tzid = CNode(name='tzid', content=gen_tz_id(tz))
        tz.add_child(tzid)

        old = None
        for t in self.timezones.children:
            if tzid.content == t.search('tzid').content:
                old = t

        if not old:
            self.timezones.add_child(tz)

        return tzid.content

    def run(self, calendaritems=None):
        """Run this multiple times (with calendaritems specified) to
        add more items to a calendar
        """
        if calendaritems:
            self.ews_calendaritems = calendaritems

        for eci in self.ews_calendaritems:
            ci = self.visit(eci)
            self.events.add_child(ci)

        return self.calendar

    def visit_CalendarItem(self,eci):
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

            # Use localtime if tz is defined:
            timeconv = xsdt2local_dt
        else:
            timeconv = xsdt2datetime

        allday = eci.search('IsAllDayEvent')
        if allday and allday.content == 'true':
            # Manual conversion of start and end
            ews_start = eci.search('Start')
            ews_end = eci.search('End')

            n_startd = timeconv(ews_start.content)
            new_start = date(n_startd.year, n_startd.month, n_startd.day + 1)
            
            if ews_end:
                n_endd = timeconv(ews_start.content)
                new_end = date(n_endd.year, n_endd.month, n_endd.day + 1)
            else:
                n_endd = timeconv(ews_start.content)
                new_end = date(n_endd.year, n_endd.month, n_endd.day + 2)

            ci.attr['start'] = new_start
            ci.attr['end'] = new_end
        else:
            conv('Start', 'start', timeconv)
            conv('End', 'end', timeconv)

        conv('Subject', 'summary', identity)
        conv('Sensitivity', 'class', sensitivity2class)
        conv('Location', 'location', identity)
        conv('DateTimeCreated', 'timestamp', timeconv)
        conv('Body', 'description', identity)


        itemid = eci.search('ItemId')
        if itemid:
            itemid_e = CNode('exchange_id')
            itemid_e.attr['id'] = itemid.attr['Id']
            itemid_e.attr['changekey'] = itemid.attr['ChangeKey']
            ci.add_child(itemid_e)

        return ci

    def visit_any(self,eci):
        """Copy the entire tree from here"""
        if eci.name == 'MeetingTimeZone':
            new_name = 'TimeZone'
        else:
            new_name = eci.name

        ci = CNode(name=new_name)
        ci.content = eci.content

        for c in eci.children:
            ci.add_child(self.visit(c))

        return ci


