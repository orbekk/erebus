# -*- coding: utf-8 -*-
from XMLObject import *
from xml.etree import ElementTree as ET
from helper.etsearch import elementsearch
from namespaces import *

class Recurrence(XMLObject):
    children = []
    
    def __init__(self, et):
        XMLObject.__init__(self,et)
