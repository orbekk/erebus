import re
from icalendar import UTC, LocalTimezone, FixedOffset, vDatetime, vDDDTypes
from datetime import datetime, timedelta

def ical2xsdt(t):
    """
    Conversion from iCalendar time to xs:dateTime
    """
    # It seems a bit random what type we get here. TODO: Why?
    if type(t) == list:
        t = t[0]
    
    if type(t) != datetime:
        ical_time = t.ical()
        dt = vDatetime.from_ical(ical_time)
    else:
        dt = t
    return datetime2xsdt(dt)

def datetime2xsdt(time):
    """
    Conversion from python's datetime to xs:dateTime
    """
    if time.tzinfo == UTC:
        tzinfo = "Z"
    else:
        ## In case of a local timezone, we will add MeetingTimeZone,
        ## so just treat it as a local xs:time
        tzinfo = ""
        # tzinfo = time.tzinfo
        # if not tzinfo: tzinfo = LocalTimezone()
        # 
        # delta = tzinfo.utcoffset(time)
        # 
        # if delta.days < 0:
        #     # timedelta = wierd format
        #     sign = '-'
        #     s = delta.seconds - 86400
        # else:
        #     sign = '+'
        #     s = delta.seconds
        # 
        # h = s / 3600
        # m = s % 3600
        # tzinfo = "%s%02d:%02d" %(sign, h, m)

    format = "%04d-%02d-%02dT%02d:%02d:%02d%s"
    dt = format %(time.year, time.month, time.day, time.hour, time.minute,
                  time.second, tzinfo)

    return dt

def xsdt2datetime(time):
    """
    Conversion from xs:dateTime to python's datetime
    """
    #                year   month   day    hour   min    sec   secfrac   tz
    p = re.compile('(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)(?:\.\d+)?(.*)$')
    m = p.match(time)
    if m == None:
        raise ValueError("Invalid date format")
    m = m.groups()

    if (m[6] == "Z"):   tzinfo = UTC
    elif (m[6] == ""):  tzinfo = LocalTimezone()
    else:
        p = re.compile('([+-])(\d\d):?(.*)$')
        tz = p.search(m[6]).groups()

        offset = int(tz[2])
        offset += int(tz[1]) * 60
        
        if tz[0] == '-':
            offset *= -1
        
        tzinfo = FixedOffset(offset, "Unknown")

    return datetime(int(m[0]), int(m[1]), int(m[2]), int(m[3]),
                    int(m[4]), int(m[5]), tzinfo=tzinfo)


def xs_date2datetime(str):
    m = re.match('(\d{4})-(\d\d)-(\d\d)(Z)?', str)
    if m == None:
        raise ValueError("Invalid date format")
    m = m.groups()

    if (m[3] == 'Z'): tzinfo = UTC
    else:             tzinfo = LocalTimezone()

    return datetime(int(m[0]), int(m[1]), int(m[2]), tzinfo=tzinfo)

def xs_dateTime2xs_date(str):
    """
    Conversion from xs:dateTime to xs:date
    """
    return str.split('T')[0]

def xs_dateTime2xs_time(str):
    """
    Conversion from xs:dateTime to xs:date
    """
    return str.split('T')[1]

def weekday_ical2xml(weekday):
    """
    Conversion from ical days (MO, TU, ...) to xml days (Monday,
    Tuesday, ...)
    """
    tab = {
        'MO' : 'Monday',
        'TU' : 'Tuesday',
        'WE' : 'Wednesday',
        'TH' : 'Thursday',
        'FR' : 'Friday',
        'SA' : 'Saturday',
        'SU' : 'Sunday'
        }
    if tab.has_key(weekday): return tab[weekday]
    else:                    return None

def weekday_xml2ical(weekday):
    """
    Conversion from xml days (Monday, Tuesday, ...) to ical days (MO,
    TU, ...)
    """
    tab = {
        'Monday'    : 'MO',
        'Tuesday'   : 'TU',
        'Wednesday' : 'WE',
        'Thursday'  : 'TH',
        'Friday'    : 'FR',
        'Saturday'  : 'SA',
        'Sunday'    : 'SU'
        }
    if tab.has_key(weekday): return tab[weekday]
    else:                    return None

def dt2xml_weekday(dt):
    ar = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
          'Saturday', 'Sunday']

    return ar[dt.weekday()]

def xs_duration2timedelta(dur):
    d = vDDDTypes.from_ical(dur)
    return d
#     m = re.search('T(\d+H)(\d+M)(\d+S)', dur)

#     if m == None:
#         return timedelta(0)
#     else:
#         tf = m.groups()
#         secs = 0
#         if tf[0]: secs += tf[0] * 3600
#         if tf[1]: secs += tf[1] *   60
#         if tf[2]: secs += tf[2]
        
#         return timedelta(secs)

    
    
    
