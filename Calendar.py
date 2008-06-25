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
        items = elementsearch(et, t('CalendarItem')).parent
        XMLObject.__init__(self, items)
        #self._make_children('calendaritems', t('CalendarItem'), CalendarItem)

    def add_calendaritem(self, item):
        self.et.append(item.et)
        self.calendaritems.append(item)

    def remove_calendaritem(self, item):
        # Add parents to all elements:
        elementsearch(self.et, None)
        item.et.parent.remove(item.et)
        self.calendaritems.remove(item)
