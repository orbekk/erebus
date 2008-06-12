from xml.etree import ElementTree as ET
from helper.etsearch import elementsearch
from helper.timeconv import *
from helper.id import identity
from namespaces import *
from Queue import Queue
from icalendar import Event
from icalendar import Calendar as ICal
from datetime import datetime
import re

class ExchangeItem(object):
    def __init__(self, et):
        self.et = et

    def get(self, attr):
        """
        m_Element: get the text of Element in the message namespace
        t_Element: same, but in the target namespace
        [mt]_Element_Attr: get the attribute Attr in Element
        """

        print "getattr: " + attr

        p = re.compile("([tm]):")
        if p.match(attr):
            splt = attr.split(":")
            if len(splt) == 2:
                ns, elem = splt
            elif len(splt) == 3:
                ns, elem, att = splt
                
            if ns == "m": ns = messages
            if ns == "t": ns = types

            e = self.search(with_ns(ns, elem))

            if e != None:
                if len(splt) == 2:
                    return e.text
                elif len(splt) == 3:
                    a = e.attrib[att]
                    if a != None:
                        return a
        
        return None
    
    def searchAll (self, tag, et=None):
        if et == None: et = self.et
        items = elementsearch(et, tag, True)
        return items

    def search(self, tag, et=None):
        if et == None: et = self.et
        item = elementsearch(et, tag)
        return item

    def toICal(self):
        e = Event()

        # - xml_e is an element in the form get() accepts
        # - ical_e is the corresponding elementname in the iCalendar format
        # - f in the transistion function from xml to iCalendar, such that
        #   f(self.get(xml_e)) is the value of ical_e
        #
        # Subclasses should override this method whenever it's not
        # flexible enough
        #
        for xml_e,ical_e,f in self.trans_xml2ical:
            xml_e = self.get(xml_e)
            if xml_e:
                e.add(ical_e, f(xml_e))

        return e

class Calendar(ExchangeItem):
    @staticmethod
    def fromXML(s):
        return Calendar(ET.XML(s))

    def __init__(self, et):
        ExchangeItem.__init__(self,et)
        self.calendarItems = []
        self.__get_calendarItems()

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

class CalendarItem(ExchangeItem):
    def __init__(self, et=None):
        ExchangeItem.__init__(self,et)
        self.get_attrs()
        self.trans_xml2ical = \ # See ExchangeItem.toICal
        [ 
            ('t:Subject', 'summary', identity),
            ('t:Start',   'dtstart', xsdt2datetime),
            ('t:End',     'dtend'  , xsdt2datetime),
            ('t:DateTimeCreated', 'dtstamp', xsdt2datetime)
        ]
    

    def get_attrs(self):
        et = self.et
        if et.tag != t('CalendarItem'):
            raise Exception("Invalid item: %s, expected %s" %(et.tag, 'CalendarItem'))

#         e_id = self.search(t('ItemId'))
#         self.attrs['ItemId'] = e_id.attrib['Id']
#         self.attrs['ChangeKey'] = e_id.attrib['ChangeKey']
        
#         e_subject = self.search(t('Subject'))
#         self.attrs['Subject'] = e_subject.text

#         self.attrs['Start'] = self.search(t('Start')).text
#         self.attrs['End']   = self.search(t('End')).text
#         self.attrs['DateTimeCreated'] = self.search(t('DateTimeCreated')).text

    def toICal(self):
        e = ExchangeItem.toICal(self)

#         e.add('summary', self.get("t:Subject"))
#         e.add('dtstart', xsdt2datetime(self.get("t:Start")))
#         e.add('dtend',   xsdt2datetime(self.get("t:End")))
#         e.add('dtstamp', xsdt2datetime(self.get("t:DateTimeCreated")))
        e['uid'] = "%s.%s@hig.no" %(self.get("t:ItemId:Id"),
                                    self.get("t:ItemId:ChangeKey"))

        return e

#     @staticmethod
#     def transform(

#     @staticmethod
#     def fromICal(event):
        
        
