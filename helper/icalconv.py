from icalendar import *
from CNode import *
from hashlib import sha1

#####
# Misc. iCalendar conversion functions
#

def class2sensitivity(cl):
    sens = { 'PUBLIC'       : 'Normal',
             'PRIVATE'      : 'Private',
             'CONFIDENTIAL' : 'Confidential' }

    if sens.has_key(cl): return sens[cl]
    else:                return None

def sensitivity2class(s):
    cs = { 'Normal'         : 'PUBLIC',
           'Personal'       : 'PRIVATE', # loosing information here.
           'Private'        : 'PRIVATE',
           'Confidential'   : 'CONFIDENTIAL' }

    if cs.has_key(s): return cs[s]
    else:             return None

def vDDD2dt(vd):
    return vd.dt

def dt2vDDD(dt):
    return vDDDTypes(dt)

def gen_tz_id(tz):
    """Generate a SHA1 sum of the timezone"""
    s = str(tz)
    return sha1(s).hexdigest()

