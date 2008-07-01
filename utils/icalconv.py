# -*- coding: utf8 -*-
from icalendar import Calendar as ICal
from CNode2StringVisitor import *
from cnodegen import *
from CNode import *
from ICS2ErebusVisitor import *
import sys

sys.path.append('../')
    
if len(sys.argv) != 2:
    print 'Usage: python %s <ical file>' % sys.argv[0]
    sys.exit()

f = sys.argv[1]
cont = open(f).read()
c = ICal.from_string(cont)
cnode = ical2cnode(c)

visitor = ICS2ErebusVisitor(cnode)
ecal = visitor.visit_start()
print CNode2StringVisitor().visit(ecal)
