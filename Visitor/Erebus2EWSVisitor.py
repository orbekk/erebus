from Visitor.CNodeVisitor import *
from CNode import *
from namespaces import *
from helper.id import identity
from helper.icalconv import *
from helper.timeconv import *

class Erebus2EWSVisitor(CNodeVisitor):

    def __init__(self,cnode):
        self.ebus = cnode
        self.items = CNode(name='Items')

    def run(self):
        self.accept(self.ebus, 'timezones')
        self.accept(self.ebus, 'events')

        return self.items

    def visit_timezones(self, cnode):
        pass

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

        conv('summary', 'Subject', identity)
        conv('class', 'Sensitivity', class2sensitivity)
        conv('description', 'Body', identity)
        conv('start', 'Start', ical2xsdt)
        conv('end', 'End', ical2xsdt)
        conv('location', 'Location', identity)

        body_e = item.search('Body')
        if body_e:
            body_e.attr['BodyType'] = 'Text'

        rec = self.accept1(cnode, 'Recurrence')
        item.add_child(rec)

        return item

    def visit_any(self,eci):
        """Copy the entire tree from here"""
        new_name = eci.name

        ci = CNode(name=new_name)
        ci.content = eci.content

        for c in eci.children:
            ci.add_child(self.visit(c))

        return ci
