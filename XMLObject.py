from xml.etree import ElementTree as ET
from helper.etsearch import *
from namespaces import *

import re

class MissingVisitor(Exception):
    def __init__(self, visitor):
        self.msg = str

    def __str__(self):
        return "Visitor %s missing" % self.visitor

class XMLObject(object):

    def __init__(self, et):
        self.et = et
        self.__make_children()

    def __make_children(self):
        children = self.children

        for attr, xml_name, attr_class in children:
            items = elementsearch(self.et, xml_name, all=True, depth=1)

#             print "%s search(%s), %d items" %(self.et.tag, xml_name, len(items))
#             if len(items) == 0:
#                 for i in self.et:
#                     print "-", i.tag
            

            setattr(self, attr, [])
            itemlist = getattr(self, attr)
        
            for item in items:
                itemlist.append(attr_class(item))

        
    def _get(self, attr, item):
        p = re.compile("([tm]):")
        if p.match(attr):
            splt = attr.split(":")
            if len(splt) == 2:
                ns, elem = splt
            elif len(splt) == 3:
                ns, elem, att = splt
                
            if ns == "m": ns = messages
            if ns == "t": ns = types

            # TODO: search_all in case of attributes?
            e = self.search(with_ns(ns, elem))
            if item: return e

            if e != None:
                if len(splt) == 2:
                    return e.text
                elif len(splt) == 3:
                    a = e.attrib[att]
                    if a != None:
                        return a
        
        return None

    def get(self, attr):
        """
        m_Element: get the text of Element in the message namespace
        t_Element: same, but in the target namespace
        [mt]_Element_Attr: get the attribute Attr in Element
        """
        return self._get(attr, False)

    def get_item(self, attr):
        """
        Same as get, but return the element instead of the text
        """
        return self._get(attr, True)

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

    def search_all (self, tag, et=None):
        if et == None: et = self.et
        items = elementsearch(et, tag, True)
        return items

    def search(self, tag, et=None):
        if et == None: et = self.et
        item = elementsearch(et, tag)
        return item


    def __str__(self):
        return ET.tostring(self.et)
