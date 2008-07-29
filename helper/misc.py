# -*- coding: utf-8 -*-

from CNode import *

def create_exchange_id(eid, e_chkey=None):
    n = CNode('exchange_id')
    n.attr['id'] = eid
    if e_chkey:
        n.attr['changekey'] = e_chkey
    return n

