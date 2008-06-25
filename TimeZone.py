# -*- coding: utf-8 -*-
from Recurrence import *
from XMLObject import *
from xml.etree import ElementTree as ET
from helper.etsearch import elementsearch
from namespaces import *

class TimeZone(XMLObject):
    children = [
        ('recurrence', t('Recurrence'), Recurrence)
        ]
    
    def __init__(self, et):
        XMLObject.__init__(self,et)
