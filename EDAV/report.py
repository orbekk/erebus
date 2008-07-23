from DAV.errors import *
import EDAV.utils as utils
import DAV.utils
import sys
import xml.dom.minidom
import urlparse
import urllib
impl = xml.dom.minidom.getDOMImplementation()

class REPORT(object):

    def _log(self, message):
        if self.__dataclass.verbose:
            print >>sys.stderr, '>> (REPORT) %s' % message

    def __init__(self,uri,dataclass,depth,xml_query):
        self.__uri = uri
        self.__dataclass = dataclass
        self.__depth = depth
        self.__xml = xml_query

        self.parse_report()

    def parse_report(self):
        props, filter = utils.parse_report(self.__xml)
        self.__props = props
        self.__filter = filter

    def create_response(self):
        dc = self.__dataclass

        self._log('creating REPORT response')
        doc = impl.createDocument(None, 'multistatus', None)
        ms = doc.documentElement
        ms.setAttribute('xmlns:D', 'DAV:')
        ms.setAttribute('xmlns:C', 'urn:ietf:params:xml:ns:caldav')

        # Make this regardless of depth
        self.__mk_response(doc,ms,self.__uri)

        if self.__depth == "1":
            children = dc.get_childs(self.__uri)
            for c_uri in children:
                re = self.__mk_response(doc,ms,c_uri)
        
        return doc.toxml(encoding='utf-8')

    def __mk_response_helper(self,doc,href,props,status_text):
        """Add properties for __mk_response.

        props is a list of elements to be added to base_elem
        """
        if len(props) > 0:
            re = doc.createElement('D:response')
            
            # add href element
            hr = doc.createElement('D:href')
            t = doc.createTextNode(href)
            hr.appendChild(t)
            re.appendChild(hr)
            
            ps = doc.createElement('D:propstat')
            for e in props:
                ps.appendChild(e)
            re.appendChild(ps)

            status = doc.createTextNode(status_text)
            re.appendChild(status)

            return re
        else:
            return None
        
    
    def __mk_response(self,doc,base_element,uri):
        uri = self.__uri

        # get href info
        uparts=urlparse.urlparse(uri)
        fileloc=uparts[2]
        href = uparts[0]+'://'+'/'.join(uparts[1:2]) + urllib.quote(fileloc)
        
        good_props, bad_props = self.__mk_props(doc,uri)

        # TODO: Use DAV.utils stuff here
        good_response = self.__mk_response_helper(doc,href,good_props,
                                                  'HTTP/1.1 200 OK')
        bad_response = self.__mk_response_helper(doc,href,bad_props,
                                              DAV.utils.gen_estring(404))

        if good_response:
            base_element.appendChild(good_response)
        if bad_response:
            base_element.appendChild(bad_response)
                

    def __mk_props(self,doc,uri):
        """Extract properties for uri.

        Like PROPFIND.get_propvalues, we return (good_props, bad_props)
        """

        good_props = []
        bad_props = []

        nsnum = 0
        dc = self.__dataclass

        for ns,plist in self.__props.iteritems():
            nsp = "ns" + str(nsnum)
            nsnum += 1

            for prop in plist:
                p = doc.createElement(nsp + ':' + prop)
                p.setAttribute('xmlns:'+nsp, ns)
                try:
                    # Add as good property
                    r = dc.get_prop(uri,ns,prop)
                    t = doc.createTextNode(str(r))
                    p.appendChild(t)
                    good_props.append(p)
                except DAV_Error, (ec,dd):
                    # If fail, then add as bad property
                    #
                    # TODO: some error_codes may be really bad,
                    # perhaps we should abort sometimes?
                    self._log('Recieved error: ' + str(ec))
                    bad_props.append(p)

        return good_props, bad_props
