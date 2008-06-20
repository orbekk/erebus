import web
from string import join
from localpw import *
from exchangetypes import *
from soapquery import *
from web_auth import *
import xml.etree.ElementTree as ET
import icalendar
import pprint
import sys
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
                c = SoapConn("http://mail1.ansatt.hig.no:80",False,
                             auth=authorized)

                q = SoapQuery(c)
                its = q.get_all_calendar_items()
                cal = Calendar.from_xml(its)
            except:
                log("error: %s" % pp.pformat(sys.exc_info()))
                auth_fail()
                return
            log(pp.pformat(cal.tostring()))
            res = cal.to_ical().as_string()

            # web.py doesn't add Content-Length header when setting
            # Content-Type manually
            web.header('Content-Length', len(res))
            print res

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
        # log('=== PUT ===')
        # log('INPUT DATA')
        # log(web.data())

        ical = icalendar.Calendar.from_string(web.data())
        cal = Calendar.from_ical(ical)

        c = SoapConn("http://mail1.ansatt.hig.no:80",False,
                     auth=authorized)
        q = SoapQuery(c)

        newItems = cal.get_new_xmlitems(uid_ignore, allItems=True)
        oldItems = q.find_items('calendar')
        oldCal   = Calendar.from_xml(oldItems)
        
        if newItems: q.create_item(newItems)

        delete = [(i.get('t:ItemId:Id'), i.get('t:ItemId:ChangeKey'))
                  for i in oldCal.calendar_items]

        if len(delete) > 0:
            q.delete_items(delete)

        print "ok"

if __name__ == "__main__": web.run(urls, globals())
