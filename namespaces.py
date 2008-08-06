# -*- coding: utf-8 -*-
def with_ns(t, s):
    return "{%s}%s" %(t,s)

def m(s):
    return with_ns(messages, s)

def t(s):
    return with_ns(types, s)

def no_namespace(s):
    arr = s.split('}')
    if len(arr) == 2:
        return arr[1]
    else:
        return s

types    = "http://schemas.microsoft.com/exchange/services/2006/types"
messages = "http://schemas.microsoft.com/exchange/services/2006/messages"

