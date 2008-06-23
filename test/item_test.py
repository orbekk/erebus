from xml.etree import *
from soapquery import *
from exchangetypes import *
from localpw import *
from namespaces import *
from helper.etsearch import *
from unittest import TestCase
import unittest
import icalendar as ical

class SoapTest(TestCase):
    def setUp(self):
        self.c = SoapConn(host,False,username,password)
        self.q = SoapQuery(self.c)


class TestBasicOps(SoapTest):
    def testCreateItem(self):
        create_dummy_item(self.q)
        
    def testItemProps(self):
        dummy = None

        items = self.q.get_all_calendar_items()
        cal = Calendar.from_xml(items)

        for i in cal.calendar_items:
            if i.get('t:Subject') == 'Dummy Item':
                dummy = i

        self.assertNotEqual(None, dummy)
        self.assertEqual(dummy.get('t:Subject'), 'Dummy Item')
        self.assertEqual(dummy.get_item('t:Subject').text, 'Dummy Item')
        self.assertEqual(dummy.get('t:Body'), 'Dummy Body')

    def testDeleteItems(self):
        items = self.q.find_items('calendar')
        cal = Calendar.from_xml(items)
        ids = []
        for i in cal.calendar_items:
            ids.append((i.get('t:ItemId:Id'), i.get('t:ItemId:ChangeKey')))

        self.q.delete_items(ids)

        items = self.q.get_all_calendar_items()
        cal = Calendar.from_xml(items)

        self.assertEqual(0, len(cal.calendar_items))

def create_dummy_item(q):
    q.create_item("""
<t:CalendarItem>
  <t:Subject>Dummy Item</t:Subject>
  <t:Body BodyType="Text">Dummy Body</t:Body>
  <t:Start>2008-08-01T12:00:00Z</t:Start>
  <t:End>2008-08-01T14:00:00Z</t:End>
</t:CalendarItem>
""")
    
def suite():
    tests = ['testCreateItem', 'testItemProps', 'testDeleteItems']
    suite = unittest.TestSuite(map(TestBasicOps, tests))

    return suite

