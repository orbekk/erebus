from exchangetypes import *
from helper.etsearch import elementsearch
from namespaces import *
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
    cal.add_component(elem)

    c = Calendar.fromICal(cal)
    print ET.tostring(c.et)

ical2xml()

