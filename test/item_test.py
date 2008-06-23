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
    def compareFields(self, rec_type, compare_items):
        self.create_recurring_item(rec_type)
        item = self.q.find_items_with_subject(rec_type)

        cal = Calendar.from_xml(item)
        citem = cal.calendar_items[0]

        f = open('/tmp/blaff', 'w')
        fi = open('/tmp/blaff.ics', 'w')

        self.assertNotEqual(citem.get_item('t:'+rec_type), None)
        
        i_id, i_chkey = (citem.get('t:ItemId:Id'), citem.get('t:ItemId:ChangeKey'))

        # TODO: Something is wrong with the iCal representation, but
        # when converted to a string and back again, it works
        as_ical = cal.to_ical().as_string()
        ics = ical.Calendar.from_string(as_ical)
        from_ical = Calendar.from_ical(ics)
        # from_ical = Calendar.from_xml(from_ical.get_new_xmlitems(all_items=True))
        iitem = from_ical.calendar_items[0]

        f.write(from_ical.tostring())

        for item in compare_items:
            self.assertEqual(citem.get(item), iitem.get(item))

        self.q.delete_items((i_id, i_chkey))
    
    def testRelativeYearlyRecurrence(self):
        self.compareFields('RelativeYearlyRecurrence', ['DaysOfWeek',
                           'DayfOfWeekIndex'])

    def create_recurring_item(self, itemtype):

        if itemtype == 'RelativeYearlyRecurrence':
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
        else:
            raise ValueError, 'Invalid type'

def suite():
    testclasses = [TestBasicOps, TestRecurrence]
    tests = []
    for c in testclasses:
        for m in sorted(dir(c)):
            if m.startswith('test'):
                tests.append(c(m))
    
    suite = unittest.TestSuite(tests)

    return suite

