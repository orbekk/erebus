# -*- coding: utf-8 -*-

import sys
sys.path.extend(['.', '../'])

from icalendar import Calendar as ICal
from Visitor.CNode2StringVisitor import *
from cnodegen import *
from CNode import *
from Visitor.ICS2ErebusVisitor import *
    
if len(sys.argv) != 2:
    print 'Usage: python %s <ical file>' % sys.argv[0]
    sys.exit()

f = sys.argv[1]
cont = open(f).read()
c = ICal.from_string(cont)
cnode = ical2cnode(c)

visitor = ICS2ErebusVisitor(cnode)
print CNode2StringVisitor().visit(visitor.ics)
ecal = visitor.visit_start()
print CNode2StringVisitor().visit(ecal)
