# -*- coding: utf-8 -*-
from xml.etree import *
from localpw import *
from namespaces import *
from unittest import TestCase
from Backend.ExchangeBackend import *
from erebusconv import *

from Visitor import *

import icalendar
import unittest
import glob

class ExchangeBackendTest(TestCase):
    def setUp(self):
        self.b = ExchangeBackend(host=host,https=False,
                                 user=username,password=password)


    def _test_erebus_conv(self,ics):
        ebus = ICS2ErebusVisitor(ics).run()
        ics2 = Erebus2ICSVisitor(ebus).run()
        ebus2 = ICS2ErebusVisitor(ics).run()

        # TODO: this won't work. Extract properties and be a bit more
        # tolerant.
        sv = ToStringVisitor()
        self.assertEqual(sv.visit(ics), sv.visit(ics2))
        self.assertEqual(sv.visit(ebus), sv.visit(ebus2))

    def test10identity(self):
        ics_files = glob.glob('test/ics/*.ics')

        for fi in ics_files:
            f = open(fi)
            ical = icalendar.Calendar.from_string(f.read())
            ics = ical2cnode(ical)
            self._test_erebus_conv(ics)

def suite():
    testclasses = [ExchangeBackendTest]
    tests = []
    for c in testclasses:
        for m in sorted(dir(c)):
            if m.startswith('test'):
                tests.append(c(m))
    
    suite = unittest.TestSuite(tests)

    return suite

