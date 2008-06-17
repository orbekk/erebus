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
    def fromICal(ical):
        cal = Calendar(ET.Element(m('Items')))
        cal._fromICal(ical)
        return cal
    
    @staticmethod

    def fromXML(s):
        return Calendar(ET.XML(s))

    def __init__(self, et):
        ExchangeItem.__init__(self,et)
        self.calendarItems = []
        self.__get_calendarItems()
        
        self.trans_xml2ical = []
        self.trans_ical2xml = []
        self.icalClass = ICal

    def __get_calendarItems(self):
        cis = self.searchAll(t('CalendarItem'))

        for ci in cis:
            self.calendarItems.append(CalendarItem(ci))

    def toICal(self):
        cal = ICal()
        cal.add('prodid', '-//iCalendar from Exchange//hig.no//')
        cal.add('version', '2.0')

        for item in self.calendarItems:
            cal.add_component(item.toICal())

        return cal

    def _fromICal(self, ical):
        super(Calendar, self)._fromICal(ical)

        for item in ical.walk('VEVENT'):
            self.addCalendarItem(CalendarItem.fromICal(item))

    def addCalendarItem(self, item):
        self.et.append(item.et)
        self.calendarItems.append(item)

    def toNewExchangeItems(self, uid_ignore, allItems=False):
        newItems = [i.toNewExchangeItem(uid_ignore,allItems)
                    for i in self.calendarItems]
        xml = ""

        for i in newItems:
            if i != None:
                xml += ET.tostring(i)
            
        return xml
            
    
