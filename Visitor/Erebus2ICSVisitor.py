from Visitor.CNodeVisitor import *
from CNode import *
from namespaces import *
from helper.id import identity
from helper.icalconv import *
from helper.timeconv import *

class Erebus2ICSVisitor(CNodeVisitor):

    def __init__(self,cnode):
        self.ebus = cnode

    def run(self):
        self.cal = CNode('vcalendar')
        
        self.cal.attr['prodid'] = '-//Erebus//hig.no//'
        self.cal.attr['version'] = '2.0'

        for e in self.accept(self.ebus, 'event'):
            self.cal.add_child(e)

        return self.cal

    def visit_event(self,cnode):
        e = CNode('vevent')

        def conv(ebus, icaln, f):
            if not cnode.attr.has_key(ebus): return
            ebus_v = cnode.attr[ebus]
            new = f(ebus_v)
            #if not new: return

            e.attr[icaln] = new
            
        conv('summary', 'summary', identity)
        conv('start', 'dtstart', dt2vDDD)
        conv('end', 'dtend', dt2vDDD)
        conv('class', 'class', identity)
        conv('location', 'location', identity)
        conv('timestamp', 'dtstamp', dt2vDDD)
        conv('description', 'description', identity)

        return e
