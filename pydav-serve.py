# -*- coding: utf-8 -*-
import sys

import getopt, sys, os
import BaseHTTPServer

try:
    import DAV
except ImportError:
    print 'DAV package not found! Please install into site-packages or set PYTHONPATH!'
    sys.exit(2)

from DAV.utils import VERSION, AUTHOR

from PyDAVServer.fileauth import DAVAuthHandler
from PyDAVServer.mysqlauth import MySQLAuthHandler
from EDAV.ExchangeHandler import ExchangeHandler
from EDAV.ErebusAuthHandler import ErebusAuthHandler

from DAV.INI_Parse import Configuration

def runserver(
         host='localhost', port = 8008,
         verbose = False,
         handler = ErebusAuthHandler,
         server = BaseHTTPServer.HTTPServer):

    host = host.strip()
   
    # basic checks against wrong hosts
    if host.find('/') != -1 or host.find(':') != -1:
        print >>sys.stderr, '>> ERROR: Malformed host %s' % host
        return sys.exit(233)

    # dispatch directory and host to the filesystem handler
    # This handler is responsible from where to take the data
    handler.IFACE_CLASS = ExchangeHandler(
        uri = "http://%s:%s/" %(host, port),
        verbose=verbose)

    # put some extra vars
    handler.verbose = verbose
   
    # initialize server on specified port
    runner = server( (host, port), handler )
    print >>sys.stderr, '>> Listening on %s (%i)' % (host, port)

    if verbose:
        print >>sys.stderr, '>> Verbose mode ON'

    print ''

    try:
        runner.serve_forever()
    except KeyboardInterrupt:
        print >>sys.stderr, '\n>> Killed by user'

usage = """Erebus WebDAV server (version %s)

Usage: ./pydav-serve [OPTIONS]
Parameters:
    -H, --host      Host where to listen on (default: localhost)
    -P, --port      Port to bind server to  (default: 8008)
    -v, --verbose   Be verbose
    -h, --help      Show this screen

PyWebDAV by %s
""" % (VERSION, AUTHOR)

if __name__ == '__main__':

    verbose = False
    port = 8008
    host = 'localhost'
    counter = 0

    # parse commandline
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'P:D:H:d:u:p:nvhmJi:c:', 
                ['host=', 'port=', 'help', 'verbose'])
    except getopt.GetoptError, e:
        print usage
        print '>>>> ERROR: %s' % str(e)
        sys.exit(2)
    
    for o,a in opts:
        if o in ['-H', '--host']:
            host = a

        if o in ['-P', '--p']:
            port = a

        if o in ['-v', '--verbose']:
            verbose = True

        if o in ['-h', '--help']:
            print usage
            sys.exit(2)

    if type(port) == type(''):
        port = int(port.strip())

    class DummyConfigDAV:
        verbose = verbose
        port = port
        host = host

    class DummyConfig:
        DAV = DummyConfigDAV()

    conf = DummyConfig()

    handler = ErebusAuthHandler
    handler._config = conf

    runserver(host, port, verbose, handler=handler)

