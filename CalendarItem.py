# -*- coding: utf-8 -*-
from XMLObject import *
from TimeZone import *
from Recurrence import *

from xml.etree import ElementTree as ET
from helper.etsearch import elementsearch
from namespaces import *

class CalendarItem(XMLObject):
    children = [
        ('timezone', t('MeetingTimeZone'), TimeZone),
        ('recurrence', t('Recurrence'), Recurrence)
        ]

    def __init__(self, et):
        XMLObject.__init__(self,et)

        self.check_item()
        #self._make_children('timezone', t('MeetingTimeZone'), TimeZone)
        #self._make_children('recurrence', t('Recurrence'), Recurrence)
        
    def check_item(self):
        if self.et.tag != t('CalendarItem'):
            raise ValueError, "Invalid item %s, expected %s" \
                  % (self.et.tag, t('CalendarItem'))
            
