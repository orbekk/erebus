def with_ns(t, s):
    return "{%s}%s" %(t,s)

def m(s):
    return with_ns(messages, s)

def t(s):
    return with_ns(types, s)

types    = "http://schemas.microsoft.com/exchange/services/2006/types"
messages = "http://schemas.microsoft.com/exchange/services/2006/messages"
