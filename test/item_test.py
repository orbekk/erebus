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
    def test10CreateItem(self):
        self.create_dummy_item()
        
    def test20ItemProps(self):
        xmlcal = self.q.find_items_with_subject('Dummy Item')
        cal = Calendar.from_xml(xmlcal)
        dummy = cal.calendar_items[0]

        self.assertNotEqual(None, dummy)
        self.assertEqual(dummy.get('t:Subject'), 'Dummy Item')
        self.assertEqual(dummy.get_item('t:Subject').text, 'Dummy Item')
        self.assertEqual(dummy.get('t:Body'), 'Dummy Body')

    def test30DeleteItems(self):
        items = self.q.find_items('calendar')
        cal = Calendar.from_xml(items)
        ids = []
        for i in cal.calendar_items:
            ids.append((i.get('t:ItemId:Id'), i.get('t:ItemId:ChangeKey')))

        self.q.delete_items(ids)

        items = self.q.get_all_calendar_items()
        cal = Calendar.from_xml(items)

        self.assertEqual(0, len(cal.calendar_items))

    def create_dummy_item(self):
        self.q.create_item("""
    <t:CalendarItem>
      <t:Subject>Dummy Item</t:Subject>
      <t:Body BodyType="Text">Dummy Body</t:Body>
      <t:Start>2008-08-01T12:00:00Z</t:Start>
      <t:End>2008-08-01T14:00:00Z</t:End>
    </t:CalendarItem>
    """)


class TestRecurrence(SoapTest):
    def testRelativeYearlyRecurrence(self):
        self.create_recurring_item()
        item = self.q.find_items_with_subject('RelativeYearlyRecurrence')

        cal = Calendar.from_xml(item)
        citem = cal.calendar_items[0]

        f = open('/tmp/blaff', 'w')

        self.assertNotEqual(citem.get_item('t:RelativeYearlyRecurrence'), None)
        
        i_id, i_chkey = (citem.get('t:ItemId:Id'), citem.get('t:ItemId:ChangeKey'))

        from_ical = Calendar.from_ical(cal.to_ical())
        from_ical = Calendar.from_xml(from_ical.get_new_xmlitems(all_items=True))
        iitem = from_ical.calendar_items[0]

        f.write(iitem.tostring())

        self.assertEqual(citem.get('t:DaysOfWeek'), iitem.get('t:DaysofWeek'))
        self.assertEqual(citem.get('t:Month'), iitem.get('t:Month'))

    def create_recurring_item(self):
        self.q.create_item("""
        <t:CalendarItem>
          <t:Subject>RelativeYearlyRecurrence</t:Subject>
          <t:Recurrence>
            <t:RelativeYearlyRecurrence>
              <t:DaysOfWeek>Tuesday</t:DaysOfWeek>
              <t:DayOfWeekIndex>Second</t:DayOfWeekIndex>
              <t:Month>August</t:Month>
            </t:RelativeYearlyRecurrence>
            <t:NoEndRecurrence>
              <t:StartDate>2008-06-23Z</t:StartDate>
            </t:NoEndRecurrence>
          </t:Recurrence>
        </t:CalendarItem>
        """)

def suite():
    testclasses = [TestBasicOps, TestRecurrence]
    tests = []
    for c in testclasses:
        for m in sorted(dir(c)):
            if m.startswith('test'):
                tests.append(c(m))
    
    suite = unittest.TestSuite(tests)

    return suite

