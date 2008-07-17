# -*- coding: utf-8 -*-

# Import events from an ics file into Exchange

import sys
sys.path.extend(['.', '../'])

from Backend.ExchangeBackend import *
from icalendar import Calendar as ICal
from Visitor.ToStringVisitor import *
from Visitor.ICS2ErebusVisitor import *
from Visitor.Erebus2ICSVisitor import *
from erebusconv import *
from CNode import *
from localpw import *

    
if len(sys.argv) != 2:
    print 'Usage: python %s <ical file>' % sys.argv[0]
    sys.exit()

f = sys.argv[1]
cont = open(f).read()
c = ICal.from_string(cont)
ctree = ical2cnode(c)

erebus = ICS2ErebusVisitor(ctree).run()

b = ExchangeBackend(host=host,https=False,user=username,password=password)
b.create_item(erebus)
