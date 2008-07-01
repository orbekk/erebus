from icalendar import Calendar as ICal
from icalendar.cal import Component
from CNode import *
from CNode2StringVisitor import *
import sys

def ical2cnode(ical):
    r = CNode(name=ical.name)

    for k,v in ical.iteritems():
        r.attr[k] = v

    for child in ical.walk():
        if child == ical: continue

        cnode = ical2cnode(child)
        if cnode.content != '':
            r.add_child(cnode)

    return r

def xml2cnode(xml):
    r = CNode(name=xml.tag)
    r.content = xml.text

    for k,v in xml.attrib.iteritems():
        r.attr[k] = v

    for c in xml.getchildren():
        e = xml2cnode(c)
        r.add_child(e)

    return r
