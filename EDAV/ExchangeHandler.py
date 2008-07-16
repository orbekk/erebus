from DAV.iface import *
from DAV.errors import *
from DAV.constants import COLLECTION, OBJECT

from Backend.ExchangeBackend import *
from Visitor.Erebus2ICSVisitor import *
from erebusconv import *

from localpw import *

import sys
import os
import urlparse

class ExchangeHandler(dav_interface):
    def __init__(self,uri,verbose=False):
        self.baseuri = uri
        self.verbose = verbose

    def _log(self, message):
        if self.verbose:
            print >>sys.stderr, '>> (DAVExchange) %s' % message

    def _get_dav_getcontenttype(self,uri):
        path = self.uri2local(uri)

        content_types = {
            '/info': 'text/plain',
            '/calendar/exchange.ics': 'text/calendar'
            }

        if content_types.has_key(path):
            return content_types[path]

        raise DAV_NotFound, 'Could not find %s' % uri

    def get_data(self,uri):
        path = self.uri2local(uri)

        if path == '/info':
            return str(self.handler.headers['Authorization'])

        if path == '/calendar/exchange.ics':
            # Get auth string from handler
            auth = ('Authorization', self.handler.headers['Authorization'])

            try:
                b = ExchangeBackend(host=host,https=False,auth=auth)
                its = b.get_all_items()
                ics = Erebus2ICSVisitor(its).run()
                ics = cnode2ical(ics).as_string()
            except QueryError, e:
                if e.status == 401:
                    self.handler.send_autherror(401,"Authorization Required")
                    return
                raise e

            return ics

        raise DAV_NotFound


    def uri2local(self,uri):
        """ map uri in baseuri and local part """

        uparts=urlparse.urlparse(uri)
        fileloc=uparts[2]
        return fileloc

    def local2uri(self,filename):
        """ map local filename to self.baseuri """

        uri=urlparse.urljoin(self.baseuri,filename)
        return uri
