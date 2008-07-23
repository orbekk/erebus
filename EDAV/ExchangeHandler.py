from DAV.iface import *
from DAV.errors import *
from DAV.constants import COLLECTION, OBJECT, CALENDAR

from Backend.ExchangeBackend import *
from Visitor import *
from erebusconv import *

from localpw import *

from hashlib import sha1
import sys
import os
import urlparse
import icalendar

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

    def _get_dav_resourcetype(self,uri):
        path = self.uri2local(uri)

        self._log("getting resourcetype for '%s'" % path)

        if path == '/':
            return COLLECTION
        elif path == '/calendar/':
            return CALENDAR        
        elif path == '/info' or path == '/calendar/exchange.ics':
            return OBJECT
        else:
            raise DAV_NotFound

    def _get_dav_getetag(self,uri):
        # not good :-p
        self._log('getting getetag for %s' % uri)
        try:
            data = self.get_data(uri)
        except DAV_Error, (ec,dd):
            if ec == 401:
                raise DAV_Forbidden
            raise
        self._log('got here')
        return sha1(data).hexdigest()

    def get_childs(self,uri):
        path = self.uri2local(uri)

        self._log("getting children of '%s'" % path)

        filelist = []

        if path == '/':
            filelist.append(self.local2uri('/'))
            filelist.append(self.local2uri('calendar'))
            filelist.append(self.local2uri('info'))
        elif path == '/calendar/':
            filelist.append(self.local2uri('/calendar/exchange.ics'))

        return filelist

    def get_data(self,uri):
        path = self.uri2local(uri)

        if path == '/info':
            return str(dir(self.handler)) 

        if path == '/calendar/exchange.ics' or path == '/calendar/':
            # Get auth string from handler
            auth = ('Authorization', self.handler.headers['Authorization'])

            try:
                b = ExchangeBackend(host=host,https=False,auth=auth)
                its = b.get_all_items()
                ics = Erebus2ICSVisitor(its).run()
                ics = cnode2ical(ics).as_string()
            except QueryError, e:
                if e.status == 401:
                    self._log('Authorization failed with auth header %s' %
                              self.handler.headers['Authorization'])
                    print e
                    raise DAV_Error, 401
                raise e

            return ics

        raise DAV_NotFound

    def put(self,uri,data,content_type=None):
        path = self.uri2local(uri)

        if path == '/calendar/exchange.ics':
            auth = ('Authorization', self.handler.headers['Authorization'])
            self._log('Uploading items')

            try:
                # Flush old items and upload new calendar                
                b = ExchangeBackend(host=host,https=False,auth=auth)
                old_itemids = b.get_all_item_ids()

                ical = icalendar.Calendar.from_string(data)
                ics = ical2cnode(ical)
                new_items = ICS2ErebusVisitor(ics).run()
                
                b.create_item(new_items)

                if old_itemids.search('event'):
                    # At least one old item
                    b.delete_item(old_itemids)

                return "Sucessfully uploaded calendar"

            except QueryError, e:
                if e.status == 401:
                    self.handler.send_autherror(401,"Authorization Required")
                    return

        return DAV_Forbidden


    def uri2local(self,uri):
        """ map uri in baseuri and local part """

        uparts=urlparse.urlparse(uri)
        fileloc=uparts[2]
        return fileloc

    def local2uri(self,filename):
        """ map local filename to self.baseuri """

        uri=urlparse.urljoin(self.baseuri,filename)
        return uri
