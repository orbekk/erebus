import re
from icalendar import UTC, LocalTimezone, FixedOffset, vDatetime
from datetime import datetime

def ical2xsdt(t):
    """
    Conversion from iCalendar time to xs:dateTime
    """
    ical_time = t.ical()
    dt = vDatetime.from_ical(ical_time)
    return datetime2xsdt(dt)

def datetime2xsdt(time):
    """
    Conversion from python's datetime to xs:dateTime
    """
    if time.tzinfo == UTC:
        tzinfo = "Z"
    else:
        tzinfo = time.tzinfo
        if not tzinfo: tzinfo = LocalTimezone()

        delta = tzinfo.utcoffset(time)

        if delta.days < 0:
            # timedelta = wierd format
            sign = '-'
            s = delta.seconds - 86400
        else:
            sign = '+'
            s = delta.seconds

        h = s / 3600
        m = s % 3600
        tzinfo = "%s%02d:%02d" %(sign, h, m)

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
        raise Exception("Invalid date format")
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
