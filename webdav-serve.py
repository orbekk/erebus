import web
from string import join
from localpw import *
from exchangetypes import *
from soapquery import *
from web_auth import *

web.webapi.internalerror = web.debugerror

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
        log('=== GET ===')
        log(web.ctx.env)
        log(web.data())

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
                cal = Calendar.fromXML(its)
            except:
                auth_fail()
                return
            print cal.toICal().as_string()
        else:
            web.notfound()

    def REPORT(self, url=None):
        log('=== REPORT ===')
        log(web.ctx.env)
        log(web.data())
        web.notfound()

    def PROPFIND(self, url=None):
        log('=== PROPFIND ===')
        log(web.ctx.env)
        log(web.data())
        web.notfound()

    def PUT(self, url=None):
        log('=== PUT ===')
        log(web.ctx.env)
        log(web.data())

        # TODO: Stappe ting opp i Exchange

        print "ok"

if __name__ == "__main__": web.run(urls, globals())
