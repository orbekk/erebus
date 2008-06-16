import web
from string import join
from localpw import *
from exchangetypes import *
from soapquery import *
from web_auth import *
import xml.etree.ElementTree as ET
import icalendar

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
#         log(web.ctx.env)
#         log(web.data())

        authorized = auth()
        if not authorized:
            auth_fail()
            return

        if url == "exchange.ics":
            try:
                c = SoapConn("http://mail1.ansatt.hig.no:80",False,
                             auth=authorized)

                q = SoapQuery(c)
                its = q.findItems('calendar')
                log(its)
                cal = Calendar.fromXML(its)
            except:
                auth_fail()
                return
            res = cal.toICal().as_string()
            web.header('Content-Length', len(res))
            print res
        else:
            web.notfound()

    def REPORT(self, url=None):
        web.header('DAV', dav_header)
        log('=== REPORT ===')
#         log(web.ctx.env)
#         log(web.data())
        web.notfound()

    def PROPFIND(self, url=None):
        web.header('DAV', dav_header)
        log('=== PROPFIND ===')
#         log(web.ctx.env)
#         log(web.data())

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
        authorized = auth()
        if not authorized:
            auth_fail()
            return
        
        web.header('DAV', dav_header)
        log('=== PUT ===')
#         log('INPUT DATA')
#         log(web.data())

        ical = icalendar.Calendar.from_string(web.data())
        cal = Calendar.fromICal(ical)

        c = SoapConn("http://mail1.ansatt.hig.no:80",False,
                     auth=authorized)
        q = SoapQuery(c)
        newItems = cal.toNewExchangeItems(uid_ignore)
        if newItems: q.createItem(newItems)

        print "ok"

if __name__ == "__main__": web.run(urls, globals())
