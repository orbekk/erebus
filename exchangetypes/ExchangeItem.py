from xml.etree import ElementTree as ET
from helper.etsearch import elementsearch
from helper.timeconv import *
from helper.id import identity
from namespaces import *
from Queue import Queue
from icalendar import Event
from icalendar import Calendar as ICal
from datetime import datetime
import helper.icalconv as icalconv
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

        p = re.compile("([tm]):")
        if p.match(attr):
            splt = attr.split(":")
            if len(splt) == 2:
                ns, elem = splt
            elif len(splt) == 3:
                ns, elem, att = splt
                
            if ns == "m": ns = messages
            if ns == "t": ns = types

            # TODO: searchAll in case of attributes?
            e = self.search(with_ns(ns, elem))

            if e != None:
                if len(splt) == 2:
                    return e.text
                elif len(splt) == 3:
                    a = e.attrib[att]
                    if a != None:
                        return a
        
        return None

    def set(self, attr, val):
        """
        attr: same as above (TODO: do we need sub elements)
        val: value to sett attr to
        """
        
        p = re.compile("([tm]):")
        if p.match(attr):
            splt = attr.split(":")
            if len(splt) == 2:
                ns, elem = splt
            elif len(splt) == 3:
                ns, elem, att = splt
                
            if ns == "m": ns = messages
            if ns == "t": ns = types

            elem = with_ns(ns, elem)

            e = self.search(elem)

            if e != None: # e claims to be a `false' :o
                if len(splt) == 2:
                    e.text = val
                elif len(splt) == 3:
                    e.attrib[att] = val
            else:
                e = ET.SubElement(self.et, elem)
                if len(splt) == 2:
                    e.text = val
                elif len(splt) == 3:
                    e.attrib[att] = val
        
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
        item = self.icalClass()

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
                item.add(ical_e, f(xml_e))

        return item


    def _fromICal(self, ical):
        # print "fromICal: ", self.__class__
        
        try:
            for ical_e,xml_e,f in self.trans_ical2xml:
                self.set(xml_e, f(ical[ical_e]))
        except KeyError:
            pass