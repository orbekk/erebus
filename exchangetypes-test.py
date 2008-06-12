from exchangetypes import *
from helper.etsearch import elementsearch
from namespaces import *
import xml.etree.ElementTree as ET

def main():
    f = open('calendar.xml')
    s = f.read()
    et = ET.XML(s)
#     ci = elementsearch(et, t('CalendarItem'))
#     calendarItem = CalendarItem(ci)

#     print calendarItem.toICal().as_string()
    calendar = Calendar(et)
    print calendar.toICal()

main()

