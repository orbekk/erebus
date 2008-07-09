# -*- coding: utf-8 -*-
import web
import pprint
pp = pprint.PrettyPrinter()

def auth_fail(realm="HiG Exchange transport"):
    web.ctx.status = '401 Authorization failed'
    web.header('WWW-Authenticate', "Basic realm=\"%s\"" %realm)
    print 'Please log in'
    return

def auth(headers):
    try:
        authorization = headers['HTTP_AUTHORIZATION']
    except KeyError:
        return None

    return ('Authorization', authorization)
        
