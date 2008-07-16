from DAV.WebDAVServer import DAVRequestHandler
import sys

class ErebusAuthHandler(DAVRequestHandler):
    """
    Always accepts, and stores the username and password so we can
    pass it to Exchange
    """
    def handle(self):
        """We need access to the handler in iface"""
        self.IFACE_CLASS.handler = self
        DAVRequestHandler.handle(self)

    def _log(self,message):
        if self.verbose:
            print >>sys.stderr, '>> (ErebusAuthHandler) %s' % message

    def get_userinfo(self,user,passwd,cmd):
        self.user = user
        self.passwd = passwd
        self._log('Authenticated user: %s' % user)
        return 1
