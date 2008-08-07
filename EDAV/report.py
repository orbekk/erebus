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
        props, filter, hrefs = utils.parse_report(self.__xml)
        self.__props = props
        self.__filter = filter
        self.__hrefs = hrefs

    def create_response(self):
        dc = self.__dataclass

        self._log('creating REPORT response')
        doc = impl.createDocument(None, 'multistatus', None)
        ms = doc.documentElement
        ms.tagName = 'D:multistatus'
        ms.setAttribute('xmlns:D', 'DAV:')
        ms.setAttribute('xmlns:C', 'urn:ietf:params:xml:ns:caldav')

        if self.__filter:
            # An associated filter; we pass it to dc
            self.__mk_response(doc, ms, self.__uri, self.__filter)

        else:
            # Make this regardless of depth
            # self.__mk_response(doc, ms, self.__uri, {})

            if self.__depth == "1":
                if self.__hrefs:
                    for href in self.__hrefs:
                        self.__mk_response(doc, ms, href, {})

                else:
                    children = dc.get_childs(self.__uri)
                    for c_uri in children:
                        # self._log('adding child with uri %s' % c_uri)
                        re = self.__mk_response(doc, ms, c_uri, {})

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
            
            pp = doc.createElement('D:prop')
            for e in props:
                pp.appendChild(e)

            ps.appendChild(pp)
            
            status = doc.createTextNode(status_text)
            ss = doc.createElement('D:status')
            ss.appendChild(status)

            ps.appendChild(ss)
            re.appendChild(ps)

            return re
        else:
            return None
        
    
    def __mk_response(self,doc,base_element,uri,filter):
        """Make a report response for an element

        filter is a hash (key,val) where key is the filter type, and
        val is the (custom) value for that type. As an example, filter
        may be {'uid',<some uid>}
        """
        
        # get href info
        uparts=urlparse.urlparse(uri)
        fileloc=uparts[2]
        href = urllib.quote(fileloc)
        # self._log('making response for %s: href %s' %(uri,href))
        
        good_props, bad_props = self.__mk_props(doc,uri,filter)

        # TODO: Use DAV.utils stuff here
        good_response = self.__mk_response_helper(doc,href,good_props,
                                                  'HTTP/1.1 200 OK')
        bad_response = self.__mk_response_helper(doc,href,bad_props,
                                              DAV.utils.gen_estring(404))

        if good_response:
            # self._log('adding good elements, props: %d' % len(good_props))
            base_element.appendChild(good_response)
        # Ignore bad props
        #if bad_response:
        #    base_element.appendChild(bad_response)
                

    def __mk_props(self,doc,uri,filter):
        """Extract properties for uri.

        Like PROPFIND.get_propvalues, we return (good_props, bad_props)

        filter: as described above
        """

        good_props = []
        bad_props = []

        nsnum = 0
        dc = self.__dataclass

        self._log(self.__props)
        
        for ns,plist in self.__props.iteritems():
            nsp = "ns" + str(nsnum)
            nsnum += 1

            for prop in plist:
                p = doc.createElement(nsp + ':' + prop)
                p.setAttribute('xmlns:'+nsp, ns)

                try:
                    ### Try as good property
                    
                    # Handle
                    caldav_ns = 'urn:ietf:params:xml:ns:caldav'
                    if ns == caldav_ns and prop == 'calendar-data':
                        data = dc.query_calendar(uri, None, filter)
                        t = doc.createTextNode(unicode(data, 'utf-8'))
                        p.appendChild(t)
                        good_props.append(p)
                    else:
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
