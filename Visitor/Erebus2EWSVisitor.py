# -*- coding: utf-8 -*-
from Visitor.CNodeVisitor import *
from CNode import *
from namespaces import *
from helper.id import identity
from helper.icalconv import *
from helper.timeconv import *
import datetime

class AddNamespaceVisitor(CNodeVisitor):
    def __init__(self,cnode,namespace):
        self.namespace = namespace
        self.cnode = cnode

    def run(self):
        self.visit(self.cnode)

    def visit_any(self,cnode):
        if not cnode.name.startswith("{"):
            cnode.name = with_ns(self.namespace, cnode.name)

        [self.visit(c) for c in cnode.children]


class Erebus2EWSVisitor(CNodeVisitor):

    def __init__(self,cnode):
        self.ebus = cnode
        self.items = CNode(name='Items')

    def run(self):
        self.accept(self.ebus, 'timezones')
        self.accept(self.ebus, 'events')

        # Add namespaces
        self.items.name = m(self.items.name)
        AddNamespaceVisitor(self.items,types).run()

        return self.items

    def visit_timezones(self, cnode):
        self.timezones = {}

        for tz in self.accept(cnode, 'TimeZone'):
            tzid = tz.search('tzid').content
            self.timezones[tzid] = tz
            tz.delete_child('tzid')

    def visit_events(self, cnode):
        item_es = self.accept(cnode, 'event')

        for i in item_es:
            self.items.add_child(i)

    def visit_event(self, cnode):
        item = CNode(name='CalendarItem')

        def conv(ebus, ews, f):
            # Convert ews[ebus] = f(ebus element)
            if not cnode.attr.has_key(ebus): return
            ebus_val = cnode.attr[ebus]
            new = f(ebus_val)
            # if not new: return
            new_e = CNode(name=ews, content=new)
            item.add_child(new_e)

        conv('summary', 'Subject', str)
        conv('class', 'Sensitivity', class2sensitivity)
        conv('description', 'Body', identity)
        conv('start', 'Start', ical2xsdt)
        conv('end', 'End', ical2xsdt)

        if type(cnode.attr['start']) == datetime.date:
            allday = CNode(name='IsAllDayEvent',content='true')
            item.add_child(allday)

        conv('location', 'Location', identity)

        body_e = item.search('Body')
        if body_e:
            body_e.attr['BodyType'] = 'Text'

        rec = self.accept1(cnode, 'Recurrence')
        if rec:
            item.add_child(rec)

        tzid = cnode.search('tzid')
        if tzid:
            tzid = tzid.content
            tz_e = self.timezones[tzid]
            tz_e = self.visit(tz_e)
            item.add_child(tz_e)

        return item

    def visit_any(self,eci):
        """Copy the entire tree from here"""
        if eci.name == 'TimeZone':
            new_name = 'MeetingTimeZone'
        else:
            new_name = eci.name

        ci = CNode(name=new_name)

        for k,v in eci.attr.iteritems():
            ci.attr[k] = v

        if eci.content != None:
            ci.content = str(eci.content)
        else:
            ci.content = None

        for c in eci.children:
            ci.add_child(self.visit(c))

        return ci
