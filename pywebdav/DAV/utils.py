#!/usr/bin/env python

"""

UTILITIES

- parse a propfind request body into a list of props

"""


from xml.dom import minidom

from string import lower, split, atoi, joinfields
import urlparse
from StringIO import StringIO

from constants import RT_ALLPROP, RT_PROPNAME, RT_PROP
from status import STATUS_CODES

VERSION = '0.8'
AUTHOR  = 'Simon Pamies <s.pamies@banality.de>'


def gen_estring(ecode):
    """ generate an error string from the given code """
    ec=atoi(str(ecode))
    if STATUS_CODES.has_key(ec):
        return "HTTP/1.1 %s %s" %(ec,STATUS_CODES[ec])
    else:
        return "HTTP/1.1 %s" %(ec)

def parse_propfind(xml_doc):
    """ parse an propfind xml file and return a list of props 

    returns:
        
        request_type            -- ALLPROP, PROPNAME, PROP
        proplist            -- list of properties found
        namespaces            -- list of namespaces found
    
    """

    doc = minidom.parseString(xml_doc)

    request_type=None
    props={}
    namespaces=[]

    if doc.getElementsByTagNameNS("DAV:", "allprop"):
        request_type = RT_ALLPROP
    elif doc.getElementsByTagNameNS("DAV:", "propname"):
        request_type = RT_PROPNAME
    else:
        request_type = RT_PROP
        e = doc.getElementsByTagNameNS("DAV:", "prop")
        for e in e[0].childNodes:
            if e.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            ns = e.namespaceURI
            ename = e.localName
            if props.has_key(ns):
                props[ns].append(ename)
            else:
                props[ns]=[ename]
                namespaces.append(ns)

    return request_type,props,namespaces


def create_treelist(dataclass,uri):
    """ create a list of resources out of a tree 

    This function is used for the COPY, MOVE and DELETE methods

    uri - the root of the subtree to flatten

    It will return the flattened tree as list

    """
    queue=[uri]
    list=[uri]
    while len(queue):
        element=queue[-1]
        if dataclass.is_collection(element):
            childs=dataclass.get_childs(element)
        else:
            childs=[]
        if len(childs):
            list=list+childs
        # update queue
        del queue[-1]
        if len(childs):
            queue=queue+childs
    return list

def is_prefix(uri1,uri2):
    """ returns 1 of uri1 is a prefix of uri2 """
    if uri2[:len(uri1)]==uri1:
        return 1
    else:
        return None

def quote_uri(uri):
    """ quote an URL but not the protocol part """
    import urlparse
    import urllib

    up=urlparse.urlparse(uri)
    np=urllib.quote(up[2])
    return urlparse.urlunparse((up[0],up[1],np,up[3],up[4],up[5]))

def get_uriparentpath(uri):
    """ extract the uri path and remove the last element """
    up=urlparse.urlparse(uri)
    return joinfields(split(up[2],"/")[:-1],"/")

def get_urifilename(uri):
    """ extract the uri path and return the last element """
    up=urlparse.urlparse(uri)
    return split(up[2],"/")[-1]

def get_parenturi(uri):
    """ return the parent of the given resource"""
    up=urlparse.urlparse(uri)
    np=joinfields(split(up[2],"/")[:-1],"/")
    return urlparse.urlunparse((up[0],up[1],np,up[3],up[4],up[5]))

### XML utilities

def make_xmlresponse(result):
    """ construct a response from a dict of uri:error_code elements """
    doc = minidom.getDOMImplementation().createDocument(None, "D:multistatus", None)
    doc.documentElement.setAttribute("xmlns:D","DAV:")

    for el,ec in result.items():
        re=doc.createElementNS("DAV:","response")
        hr=doc.createElementNS("DAV:","href")
        st=doc.createElementNS("DAV:","status")
        huri=doc.createTextNode(quote_uri(el))
        t=doc.createTextNode(gen_estring(ec))
        st.appendChild(t)
        hr.appendChild(huri)
        re.appendChild(hr)
        re.appendChild(st)
        doc.documentElement.appendChild(re)

    return doc.toxml(encoding="utf-8")
