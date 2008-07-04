from xml.etree import ElementTree as ET
from icalendar import Calendar, Event
from icalendar.cal import Component
from icalendar.cal import Component
from CNode import *
from Visitor.ToStringVisitor import *
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

def cnode2ical(cnode):
    comp = Component()

    for k,v in cnode.attr.iteritems():
        comp.add(k,v)

    for c in cnode.children:
        comp.add_component(cnode2ical(c))

    return comp

def xml2cnode(xml):
    r = CNode(name=xml.tag)
    r.content = xml.text

    for k,v in xml.attrib.iteritems():
        r.attr[k] = v

    for c in xml.getchildren():
        e = xml2cnode(c)
        r.add_child(e)

    return r

def cnode2xml(cnode):
    r = ET.Element(cnode.name)

    for k,v in cnode.attr.iteritems():
        r.set(k,v)

    for c in cnode.children:
        ch = cnode2xml(c)
        r.append(ch)

    if cnode.content:
        r.text = cnode.content

    return r
