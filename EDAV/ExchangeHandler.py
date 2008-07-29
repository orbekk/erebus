from EDAV.caldav_iface import *
from DAV.errors import *
from DAV.constants import COLLECTION, OBJECT, CALENDAR

from Backend.ExchangeBackend import *
from Visitor import *
from erebusconv import *
from helper.misc import *

from localpw import *

from hashlib import sha1
import sys
import os
import urlparse
import urllib
import icalendar
import base64

class ExchangeHandler(caldav_interface):
    """The Exchange backend for our CalDAV server
    """

    ###
    # TODO: A lot of caching could probably be done here (like, caching
    # items and item ids, which are fetched several times per query
    # right now). Need to check when this class gets created.
    
    def __init__(self,uri,verbose=False):
        self.baseuri = uri
        self.verbose = verbose

    def _log(self, message):
        if self.verbose:
            print >>sys.stderr, '>> (ExchangeHandler) %s' % message

    def query_calendar(self,uri,filter,calendar_data):
        self._log('querying for calendar data')
        return self.get_data(uri)

    def _get_dav_getcontenttype(self,uri):
        path = self.uri2local(uri)

        content_types = {
            '/info': 'text/plain',
            '/calendar/exchange.ics': 'text/calendar'
            }

        if content_types.has_key(path):
            return content_types[path]

        if path.startswith('/calendar/eid-'):
            return 'text/calendar'

        raise DAV_NotFound, 'Could not find %s' % uri

    def _get_dav_resourcetype(self,uri):
        path = self.uri2local(uri)

        self._log("getting resourcetype for '%s'" % path)

        if path == '/':
            return COLLECTION
        elif path == '/calendar/' or path == '/calendar':
            return CALENDAR        
        elif path == '/info' or path == '/calendar/exchange.ics':
            return OBJECT
        elif path.startswith('/calendar/eid-'):
            return OBJECT # TODO: what if it doesn't exist?
        else:
            raise DAV_NotFound

    def _get_dav_getetag(self,uri):
        # not good :-p
        self._log('getting getetag for %s' % uri)

        path = self.uri2local(uri)
        if path.startswith('/calendar/eid-'):
            b64 = path.split('-')[1]
            # Use the base64 encoded string as ETag
            return b64
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

        # Get auth string from handler
        auth = ('Authorization', self.handler.headers['Authorization'])

        children = []

        if path == '/':
            children.append(self.local2uri('/'))
            children.append(self.local2uri('/calendar'))
            children.append(self.local2uri('/info'))
        elif path == '/calendar/' or path == '/calendar':
            # All our calendar objects
            try:
                b = ExchangeBackend(host=host,https=False,auth=auth)
                ids = b.get_all_item_ids()
                for it in ids.search('exchange_id', all=True, keep_depth=True):
                    etag = base64.b64encode(it.attr['id'] + '.' +
                                            it.attr['changekey'])
                    children.append(self.local2uri('/calendar/eid-' + etag))
            except QueryError, e:
                if e.status == 401:
                    self._log('Authorization failed')
                    self._log(e)
                    raise DAV_Error, 401

        return children

    def get_data(self,uri):
        path = self.uri2local(uri)
        auth = ('Authorization', self.handler.headers['Authorization'])

        if path.startswith('/calendar/eid-'):
            b64 = path.split('-')[1]
            etag = base64.b64decode(b64)
            eid, e_chkey = etag.split('.')
            ei = create_exchange_id(eid, e_chkey)
            try:
                b = ExchangeBackend(host=host,https=False,auth=auth)
                it = b.get_item(ei)
                # TODO: if no item, then what?
                ics = Erebus2ICSVisitor(it).run()
                ics = cnode2ical(ics).as_string()
            except QueryError, e:
                if e.status == 401:
                    self._log('Authorization failed')
                    self._log(e)
                    raise DAV_Error, 401
                raise

            return ics

        if path == '/info':
            b = ExchangeBackend(host=host,https=False,auth=auth)
            its = b.get_all_item_ids()
            return ToStringVisitor().visit(its)

        if path == '/calendar/exchange.ics':
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

        if path.startswith('/calendar/'):
            auth = ('Authorization', self.handler.headers['Authorization'])
            self._log('Uploading items, auth: %s' % str(auth))

            try:
                # Flush old items and upload new calendar                
                b = ExchangeBackend(host=host,https=False,auth=auth)
                old_itemids = b.get_all_item_ids()

                ical = icalendar.Calendar.from_string(data)
                ics = ical2cnode(ical)
                new_items = ICS2ErebusVisitor(ics).run()
                self._log(new_items)
                
                b.create_item(new_items)

                # if old_itemids.search('event'):
                #     # At least one old item
                #     b.delete_item(old_itemids)

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
