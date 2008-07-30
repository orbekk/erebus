from xml.dom import minidom

def parse_report(xml):
    """Parse a REPORT xml string

    returns: (properties, filters)
    """
    doc = minidom.parseString(xml)

    props = {}
    filters = []

    caldav_ns = 'urn:ietf:params:xml:ns:caldav'
    xml_prop = doc.getElementsByTagNameNS('DAV:', 'prop')
    xml_filter = doc.getElementsByTagNameNS(caldav_ns, 'filter')

    for e in xml_prop[0].childNodes:
        if e.nodeType != minidom.Node.ELEMENT_NODE:
            continue

        ns = e.namespaceURI
        tag = e.localName

        if props.has_key(ns):
            props[ns].append(tag)
        else:
            props[ns] = [tag]

    # TODO: filter

    return props,xml_filter
        
