from xml.dom import minidom
from xml.etree import ElementTree as ET
from Visitor.EWS2ErebusVisitor import StripNamespaceVisitor
from Visitor.ToStringVisitor import *
from erebusconv import *

def _log(str):
    import sys
    print >>sys.stderr, '>> (utils) %s' % str

def parse_report(xml):
    """Parse a REPORT xml string

    returns: (properties, filters)
    """
    doc = minidom.parseString(xml)

    props = {}
    filters = []
    hrefs = []

    caldav_ns = 'urn:ietf:params:xml:ns:caldav'
    xml_prop = doc.getElementsByTagNameNS('DAV:', 'prop')
    xml_filter = doc.getElementsByTagNameNS(caldav_ns, 'filter')
    xml_hrefs = doc.getElementsByTagNameNS('DAV:', 'href')
    
    if len(xml_filter):
        filter = parse_filter(xml_filter[0].toxml())
    else:
        filter = {}

    for e in xml_prop[0].childNodes:
        if e.nodeType != minidom.Node.ELEMENT_NODE:
            continue

        ns = e.namespaceURI
        tag = e.localName

        if props.has_key(ns):
            props[ns].append(tag)
        else:
            props[ns] = [tag]

    for e in xml_hrefs:
        for c in e.childNodes:
            if c.nodeType != minidom.Node.TEXT_NODE:
                continue
            href = c.data
            hrefs.append(href)

    return props,filter,hrefs
        

def parse_filter(xml_string):
    """Parse a DAV::filter"""

    filter = {}

    # Use a CNode tree
    ctree = xml2cnode(ET.XML(xml_string))
    StripNamespaceVisitor().visit(ctree)

    _log(ToStringVisitor().visit(ctree))

    for e in ctree.search('comp-filter',all=True):
        # On an empty VEVENT, get all items
        if e.attr['name'] == 'VEVENT':
            if not len(e.children):
                _log('found empty VEVENT. getall!')
                return {}
                
            for f in e.search('prop-filter',all=True):
                if f.attr['name'] == 'UID':
                    # TODO: support i;ascii-casemap
                    match = f.search('text-match')
                    uid = match.content

                    if not filter.has_key('uid'):
                        filter['uid'] = []

                    filter['uid'].append(uid)

    _log(filter)

    return filter
