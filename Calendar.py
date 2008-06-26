from XMLObject import *
from CalendarItem import *
from xml.etree import ElementTree as ET
from helper.etsearch import *
from namespaces import *

class Calendar(XMLObject):
    children = [
        ('calendaritems', t('CalendarItem'), CalendarItem)
        ]
    
    def __init__(self, et):
        # Make our own root and collect all the CalendarItems
        r = ET.Element(t('Items'))
        items = elementsearch(et, t('CalendarItem'), all=True)
        for i in items:
            r.append(i)
            
        XMLObject.__init__(self, r)
        #self._make_children('calendaritems', t('CalendarItem'), CalendarItem)

    def add_calendaritem(self, item):
        self.et.append(item.et)
        self.calendaritems.append(item)

    def remove_calendaritem(self, item):
        # Add parents to all elements:
        elementsearch(self.et, None)
        item.et.parent.remove(item.et)
        self.calendaritems.remove(item)
