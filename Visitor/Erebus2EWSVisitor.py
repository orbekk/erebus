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
        self.accept(self.ebus, 'events')

        return self.items

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

        return item
