from xml.etree import ElementTree as ET
from helper.etsearch import elementsearch
from helper.timeconv import *
from helper.id import identity
from namespaces import *
from Queue import Queue
from icalendar import Event
from icalendar import Calendar as ICal
from datetime import datetime
import helper.icalconv as icalconv
import re

from exchangetypes.ExchangeItem import ExchangeItem
from exchangetypes.CalendarItem import CalendarItem

class Calendar(ExchangeItem):
    @staticmethod
    def from_ical(ical):
        """Create a Calendar from an iCalendar object"""
        cal = Calendar(ET.Element(m('Items')))
        cal._from_ical(ical)
        return cal
    
    @staticmethod

    def from_xml(s):
        """Create a Calendar from a XML string as given by exchange

        (The calendar events are created from CalendarItems in the
        XML)
        """
        return Calendar(ET.XML(s))

    def __init__(self, et):
        ExchangeItem.__init__(self,et)
        self.calendar_items = []
        self.__get_calendar_items()
        
        self.trans_xml2ical = []
        self.trans_ical2xml = []
        self.icalClass = ICal

    def __get_calendar_items(self):
        cis = self.search_all(t('CalendarItem'))

        for ci in cis:
            self.calendar_items.append(CalendarItem(ci))

    def to_ical(self):
        cal = ICal()
        cal.add('prodid', '-//iCalendar from Exchange//hig.no//')
        cal.add('version', '2.0')

        for item in self.calendar_items:
            cal.add_component(item.to_ical())

        return cal

    def _from_ical(self, ical):
        super(Calendar, self)._from_ical(ical)

        for item in ical.walk('VEVENT'):
            self.add_calendaritem(CalendarItem.from_ical(item))

    def add_calendaritem(self, item):
        self.et.append(item.et)
        self.calendar_items.append(item)

    def get_new_xmlitems(self, uid_ignore={}, allItems=False):
        """Return all items not yet in Exchange"""
        
        new_items = [i.get_new_exchangeitem(uid_ignore,allItems)
                    for i in self.calendar_items]
        xml = ""

        for i in new_items:
            if i != None:
                xml += ET.tostring(i)
            
        return xml
            
    
