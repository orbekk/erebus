from EDAV.caldav_iface import *
from DAV.errors import *
from DAV.constants import COLLECTION, OBJECT, CALENDAR

from Backend.ExchangeBackend import *
from Visitor import *
from erebusconv import *
from helper.misc import *

from localpw import *

from xml.etree import ElementTree as ET
from hashlib import sha1
import re
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

        # This is a table to keep track of client UID's (since we
        # change them, we need to know which item to give back)
        self.itemids = {}

    def _log(self, message):
        if self.verbose:
            print >>sys.stderr, '>> (ExchangeHandler) %s' % message

    def _init_backend(self):
        auth = ('Authorization', self.handler.headers['Authorization'])
        return ExchangeBackend(host=host, https=use_https, auth=auth)
    
    def query_calendar(self,uri,calendar_data,filter):
        self._log('querying for calendar data')
        
        # Convert filter to cnodes
        if filter:
            self._log('we got filter!')
            if filter.has_key('uid'):
                getuids = filter['uid']
                getall = False
            else:
                getuids = []
                getall = True
        else:
            getall = True

        if getall:
            return self.get_data(uri)
        else:
            visitor = Erebus2ICSVisitor()
            for uid in getuids:
                if self.itemids.has_key(uid):
                    ex_id = self.itemids[uid]
                else:
                    uid = uid.split('@')[0]
                    ex_id = create_exchange_id(uid)

                self._log('asked for element with uid: %s' % ex_id)

                try:
                    auth = ('Authorization', self.handler.headers['Authorization'])
                    b = ExchangeBackend(host=host,https=False,auth=auth)
                    it = b.get_item(ex_id)

                    visitor.run(it)
                except:
                    raise DAV_Error, 404

            cal = visitor.cal
            cal = cnode2ical(cal)
            return cal.as_string()

    def _get_dav_displayname(self,uri):
        return "Microsoft Exchange calendar via Erebus"

    def _get_caldav_calendar_home_set(self,uri):
        n = self._doc.createElement('D:href')
        t = self._doc.createTextNode('/calendar/')
        n.appendChild(t)
        return n

    def _get_caldav_calendar_user_address_set(self,uri):
        n = self._doc.createElement('D:href')
        t = self._doc.createTextNode('/calendar/')
        n.appendChild(t)
        return n

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


    def _get_exchange_id(self,uri):
        """Return the exchange id (*with* changekey) for an uri (this
        may either be a /calendar/eid-* uri or a uri in itemids)
        """
        path = self.uri2local(uri)
        self._log('getting etag for uri %s' % uri)

        if path.startswith('/calendar/eid-'):
            b64 = path.split('-')[1]
            eid = etag2exchange_id(b64)
            try:
                b = self._init_backend()
                it = b.get_item(eid, props=[])
                eid = it.search('exchange_id')
                return eid
            except:
                pass

        if path.startswith('/calendar/'):
            pp = path.replace('/calendar/', '', 1)
            if self.itemids.has_key(pp):
                eid = self.itemids[pp]
                return eid

        else:
            return None

    def _get_dav_getetag(self,uri):
        # not good :-p
        # self._log('getting getetag for %s' % uri)
        eid = self._get_exchange_id(uri)
        if eid:
            return exchange_id2etag(eid)

        data = self.get_data(uri)
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
                b = self._init_backend()
                ids = b.get_all_item_ids()
                for it in ids.search('exchange_id', all=True, keep_depth=True):
                    # Don't use etag as uri anymore - just the itemid
                    # etag = exchange_id2etag(it)
                    children.append(self.local2uri('/calendar/eid-' +
                                                   base64.b64encode(it.attr['id'])))
            except QueryError, e:
                if e.status == 401:
                    self._log('Authorization failed')
                    self._log(e)
                    raise DAV_Error, 401

        return children

    def get_data(self,uri):
        path = self.uri2local(uri)

        self._log('getting data for uri %s' % uri)

        try:
            if path.startswith('/calendar/eid-'):
                b64 = path.split('-')[1]
                ei = etag2exchange_id(b64)
            else:
                pp = path.replace('/calendar/', '', 1)
                pp = re.sub('\.ics$', '', pp)
                if self.itemids.has_key(pp):
                    ei = self.itemids[pp]
                else:
                    raise DAV_Error, 404

            self._log('get data with exchangeid: %s' % ei.attr['id'])
            b = self._init_backend()
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
        except TypeError, e:
            # Incorrect padding means invalid url
            raise DAV_Error, 404

        return ics

        if path == '/info':
            b = self._init_backend()
            its = b.get_all_item_ids()
            return ToStringVisitor().visit(its)

# Don't return data on a query on the collection
#         if path == '/calendar/' or path == '/calendar':
#             try:
#                 b = self._init_backend()
#                 its = b.get_all_items()
#                 ics = Erebus2ICSVisitor(its).run()
#                 ics = cnode2ical(ics).as_string()
#             except QueryError, e:
#                 if e.status == 401:
#                     self._log('Authorization failed with auth header %s' %
#                               self.handler.headers['Authorization'])
#                     print e
#                     raise DAV_Error, 401
#                 raise e
#             return ics

        raise DAV_NotFound

    def put(self,uri,data,content_type=None):
        path = self.uri2local(uri)

        if path.startswith('/calendar/'):
            auth = ('Authorization', self.handler.headers['Authorization'])
            self._log('Uploading items, auth: %s' % str(auth))

            try:
                b = self._init_backend()

                if self.handler.headers.has_key('If-None-Match') and \
                       self.handler.headers['If-None-Match'] == '*':
                    # This is a new item
                    ical = icalendar.Calendar.from_string(data)
                    ics = ical2cnode(ical)
                    new_items = ICS2ErebusVisitor(ics).run()
                    eid = b.create_item(new_items)

                    # There should only be one item here
                    ical_uid = new_items.search('event').attr['ical_uid']
                    self._log('Added uid mapping: %s -> %s' %(ical_uid, eid))
                    self.itemids[str(ical_uid)] = eid

                    self._log('Created item with id %s' % eid)
                    return 'Sucessfully uploaded calendar item'
                
                elif self.handler.headers.has_key('If-Match'):
                    # Update this item
                    self._log('Updating item!')
                    etag = self.handler.headers['If-Match']
                    if self.itemids.has_key(etag):
                        ei = self.itemids[etag]
                    else:
                        ei = etag2exchange_id(etag)

                    ical = icalendar.Calendar.from_string(data)
                    ics = ical2cnode(ical)
                    item_changes = ICS2ErebusVisitor(ics).run()

                    b.update_item(ei, item_changes)

                    raise DAV_Error, 204

            except QueryError, e:
                if e.status == 401:
                    self.handler.send_autherror(401,"Authorization Required")
                    return
                self._log(e)
                raise

        return DAV_Forbidden


    def uri2local(self,uri):
        """ map uri in baseuri and local part """

        u = urllib.unquote(uri)
        uparts=urlparse.urlparse(u)
        fileloc=uparts[2]
        return fileloc

    def local2uri(self,filename):
        """ map local filename to self.baseuri """

        uri=urlparse.urljoin(self.baseuri,filename)
        return uri

    def delone(self,uri):

        etag = self.handler.headers['If-Match']
        ei = etag2exchange_id(etag)

        try:
            auth = ('Authorization', self.handler.headers['Authorization'])
            b = self._init_backend()
            self._log('deleting %s' % str(ei))
            b.delete_item(ei)
        except QueryError, e:
            self._log(e)
            raise DAV_NotFound

        return None
        
def etag2exchange_id(b64_etag):
    etag = base64.b64decode(b64_etag)
    ss = etag.split('.')
    eid = ss[0]
    if len(ss) > 1:
        chkey = ss[1]
    else:
        chkey = None

    ei = create_exchange_id(eid, chkey)
    return ei

def exchange_id2etag(eid):
    etag = base64.b64encode(eid.attr['id'] + '.' +
                            eid.attr['changekey'])
    return etag
