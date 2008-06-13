from exchangetypes import *
from helper.etsearch import elementsearch
from namespaces import *
from datetime import datetime
import icalendar
import xml.etree.ElementTree as ET

def xml2ical():
    f = open('calendar.xml')
    s = f.read()
    et = ET.XML(s)
#     ci = elementsearch(et, t('CalendarItem'))
#     calendarItem = CalendarItem(ci)

#     print calendarItem.toICal().as_string()
    calendar = Calendar(et)
    print calendar.toICal()

def ical2xml():
    cal = icalendar.Calendar()
    elem = icalendar.Event()
    elem['uid'] = ':)'
    elem.add('summary', 'heisann hoppsann')
    elem.add('dtstart', datetime(2006, 01, 02, 14, 00))
    elem.add('dtend', datetime(2006, 01, 02, 16, 00))
    elem.add('dtstamp', datetime(2006, 01, 02, 10, 00))
    cal.add_component(elem)

    c = Calendar.fromICal(cal)
    print ET.tostring(c.et)

ical2xml()

