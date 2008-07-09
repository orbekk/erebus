# -*- coding: utf-8 -*-
import web
from string import join
from localpw import *
from web_auth import *
import xml.etree.ElementTree as ET
import icalendar
import pprint
import sys

from Backend.ExchangeBackend import *
from Visitor.Erebus2ICSVisitor import *
from Visitor.ICS2ErebusVisitor import *
from erebusconv import *
pp = pprint.PrettyPrinter()

web.webapi.internalerror = web.debugerror
uid_ignore = {}

urls = (
    '/calendar/(.*)', 'calendar',
    '/calendar', 'calendar',
    )

allowed = "OPTIONS, GET, HEAD, PUT, DELETE, PROPFIND," + \
          "MKCOL, MKCALENDAR, LOCK, UNLOCK, REPORT, PROPPATCH"

dav_header = "1, 2, calendar-access, access-control"

def log(msg):
    f = open('/tmp/log', 'a+')
    f.write(str(msg) + '\n\n')

class calendar:
    def GET(self, url=None):
        web.header('Dav', dav_header)
        web.header('ETag', 'roflbar')
        web.header('Content-Type', 'text/calendar')

        log('=== GET ===')
        # log(pp.pformat(web.ctx.env))
        # log(web.data())

        authorized = auth(web.ctx.env)
        log("Response from auth: %s" % pp.pformat(authorized))
        if not authorized:
            auth_fail()
            return

        if url == "exchange.ics":
            try:
                b = ExchangeBackend(host=host,https=False,user=username,
                                    password=password)
                its = b.get_all_items()
                ics = Erebus2ICSVisitor(its).run()
                ics = cnode2ical(ics).as_string()
            except:
                log("error: %s" % pp.pformat(sys.exc_info()))
                auth_fail()
                return
            # web.py doesn't add Content-Length header when setting
            # Content-Type manually
            web.header('Content-Length', len(ics))
            print ics

        else:
            web.notfound()

    def REPORT(self, url=None):
        web.header('DAV', dav_header)
        # log('=== REPORT ===')
        # log(web.ctx.env)
        # log(web.data())
        web.notfound()

    def PROPFIND(self, url=None):
        web.header('DAV', dav_header)
        # log('=== PROPFIND ===')
        # log(web.ctx.env)
        # log(web.data())

        web.ctx.status = "207 Multi-Status"

        print \
"""<?xml version="1.0" encoding="utf-8"?>
<multistatus xmlns="DAV:">
  <response>
    <href>/calendar/exchange.ics</href>
    <propstat>
      <prop>
        <getetag>test1234</getetag>
      </prop>
    <status>HTTP/1.1 200 OK</status>  
    </propstat>
  </response>  
</multistatus>"""

    def PUT(self, url=None):
        """
        For now, just flush the entire calendar instead of being smart
        about it. (This seems to be WebDAV's way of doing things
        anyway)
        """

        authorized = auth(web.ctx.env)
        if not authorized:
            auth_fail()
            return
        
        web.header('DAV', dav_header)
        log('=== PUT ===')
        # log('INPUT DATA')
        # log(web.data())

        ical = icalendar.Calendar.from_string(web.data())
        ics = ical2cnode(ical)
        erebus = ICS2ErebusVisitor(ics).run()

        b = ExchangeBackend(host=host,https=False,user=username,
                            password=password)

        old_items = b.get_all_item_ids()
        b.create_item(erebus)
        
        if old_items.search('event'):
            b.delete_item(old_items)

        print "ok"

if __name__ == "__main__": web.run(urls, globals())
