from EDAV.CalDAVServer import CalDAVRequestHandler
import sys

class ErebusAuthHandler(CalDAVRequestHandler):
    """
    Always accepts, and stores the username and password so we can
    pass it to Exchange
    """
    def handle(self):
        """We need access to the handler in iface"""
        self.IFACE_CLASS.handler = self
        CalDAVRequestHandler.handle(self)

    def _log(self,message):
        if self.verbose:
            print >>sys.stderr, '>> (ErebusAuthHandler) %s' % message

    def get_userinfo(self,user,passwd,cmd):
        self.user = user
        self.passwd = passwd
        self._log('Authenticated user: %s (%s)' % (user,self.headers['Authorization']))
        return 1
