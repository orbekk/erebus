import EDAV.utils as utils
import sys
import xml.dom.minidom
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
        
        # HER!
        return ":D"
    
    def __mk_response(self,doc,uri):
        uri = self.__uri

        re = doc.createElement('D:response')

        # write href information
        uparts=urlparse.urlparse(uri)
        fileloc=uparts[2]
        href=doc.createElement('D:href')
        huri=doc.createTextNode(uparts[0]+'://'+'/'.join(uparts[1:2]) + urllib.quote(fileloc))
        href.appendChild(huri)
        re.appendChild(href)

        ps = doc.createElement('D:propstat')

    def __mk_props(self,uri,doc):
        """Extract properties for uri.

        Like PROPFIND.get_propvalues, we return (good_props, bad_props)
        """

        good_props = []
        bad_props = []

        nsnum = 0
        dc = self.__dataclass

        for ns,plist in self.proplist.iteritems():
            nsp = "ns" + str(nsnum)
            nsnum += 1

            for prop in plist:
                p = doc.createElement(nsp+prop)
                p.setAttribute('xmlns'+nsp, ns)
                try:
                    # Add as good property
                    r = dc.get_prop(uri,ns,prop)
                    t = doc.createTextNode(str(r))
                    p.appendChild(t)
                    good_props.append(p)
                except DAV_Error, error_code:
                    # If fail, then add as bad property
                    #
                    # TODO: some error_codes may be really bad,
                    # perhaps we should abort sometimes?
                    bad_props.append(p)

        return good_props, bad_props
