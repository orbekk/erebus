# -*- coding: utf-8 -*-

from CNode import *

def create_exchange_id(eid, e_chkey):
    n = CNode('exchange_id')
    n['id'] = eid
    n['changekey'] = e_chkey

