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
    elem['uid'] = 'AAAUADk5NTU1NUBhbnNhdHQuaGlnLm5vAEYAAAAAAFweQ/PYr15OrbYzBHnAiuAHACOPZb+9/tdIoI9+J7qYDTsAC6b9m+QAACOPZb+9/tdIoI9+J7qYDTsADbsWUlkAAA==.DwAAABYAAAAjj2W/vf7XSKCPfie6mA07AA27FqHR@hig.no'
    elem.add('summary', 'heisann hoppsann')
    elem.add('dtstart', datetime(2006, 01, 02, 14, 00))
    elem.add('dtend', datetime(2006, 01, 02, 16, 00))
    elem.add('dtstamp', datetime(2006, 01, 02, 10, 00))
    cal.add_component(elem)

    c = Calendar.fromICal(cal)
    print ET.tostring(c.et)

    print "<ical>%s</ical>" % c.toICal()

ical2xml()

