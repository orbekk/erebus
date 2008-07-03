# -*- coding: utf-8 -*-

import sys
sys.path.extend(['.', '../'])

from icalendar import Calendar as ICal
from Visitor.ToStringVisitor import *
from Visitor.ICS2ErebusVisitor import *
from Visitor.Erebus2ICSVisitor import *
from erebusconv import *
from CNode import *

    
if len(sys.argv) != 2:
    print 'Usage: python %s <ical file>' % sys.argv[0]
    sys.exit()

f = sys.argv[1]
cont = open(f).read()
c = ICal.from_string(cont)
cnode = ical2cnode(c)

visitor = ICS2ErebusVisitor(cnode)
print ToStringVisitor().visit(visitor.ics)
print "======================================================================"
ecal = visitor.run()
print ToStringVisitor().visit(ecal)
print "======================================================================"
new_ical = Erebus2ICSVisitor(ecal).run()
print ToStringVisitor().visit(new_ical)
