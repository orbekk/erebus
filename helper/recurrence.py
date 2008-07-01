from xml.etree import ElementTree as ET
from helper.timeconv import *
from namespaces import *
from CNode import *
import datetime
import re

def rrule2recurrence(rrule, starttime):
    freq = rrule['freq'][0]
    
    if rrule.has_key('INTERVAL'):
        interval = rrule['INTERVAL'][0]
    else:
        interval = 1

    interval_e = CNode(name='Interval', content=interval)
    recurrence_e = CNode(name='Recurrence')

    if freq == 'YEARLY':
        recpattern_e = rrule2yearly_recpattern(rrule, interval_e, starttime)
        recurrence_e.add_child(recpattern_e)
        
    elif freq == 'MONTHLY':
        if  rrule.has_key('BYDAY'):
            # When more than one day, it is impossible to do in
            # Exchange (except if all days are in the same week)
            day = rrule['byday'][0]

            recpattern_e = CNode(name='RelativeMonthlyRecurrence')
            dow_e, weekindex_e = byday2rel_month(day)

            recpattern_e.add_child(interval_e)
            recpattern_e.add_child(dow_e)
            recpattern_e.add_child(weekindex_e)

            recurrence_e.add_child(recpattern_e)
        else:
            recpattern_e = CNode(name='AbsoluteMonthlyRecurrence')

            if rrule.has_key('BYMONTHDAY'):
                mday = str(rrule['BYMONTHDAY'][0])
            else:
                mday = str(starttime.day)

            dayofmonth = CNode(name='DayOfMonth',content=mday)

            recpattern_e.add_child(dayofmonth)
            recurrence_e.add_child(recpattern_e)

    elif freq == 'WEEKLY' or \
         (freq == 'DAILY' and rrule.has_key('BYDAY')):

        recpattern_e = CNode(name='WeeklyRecurrence')
        daysofweek_e = CNode(name='DaysOfWeek')

        if rrule.has_key('WKST') or rrule.has_key('BYDAY'):
            if rrule.has_key('WKST'): # TODO: really?
                ical_days = rrule['WKST']
            else:
                ical_days = rrule['BYDAY']

            days = [weekday_ical2xml(w) for w in ical_days]
            daysofweek_e.content = " ".join(days)

        else:
            wkday = dt2xml_weekday(starttime)
            daysofweek_e.content = wkday

        recpattern_e.add_child(interval_e)
        recpattern_e.add_child(daysofweek_e)

        recurrence_e.add_child(recpattern_e)


    elif freq == 'DAILY':
        recpattern_e = CNode(name='DailyRecurrence')
        recpattern_e.add_child(interval_e)
        
        recurrence_e.add_child(recpattern_e)

    return recurrence_e

def rrule2yearly_recpattern(rrule,interval_e,event_start=None):
    """Convert a YEARLY iCalendar recurrence to Erebus
    RecurrencePattern

    rrule: the iCalendar recurrence rule
    interval_e: the interval element
    """
    if rrule.has_key('byday') and rrule.has_key('bymonth'):
        recpattern = CNode(name='RelativeYearlyRecurrence')

        dow_e, weekindex_e = byday2rel_month(rrule['byday'][0])

        if rrule['bymonth']:
            m = int(rrule['bymonth'][0])
            month = ex_months[m]
        elif event_start:
            month = xsdt2ex_month(event_start)
        else:
            ValueError, "neither BYMONTH or event_start is available"

        month_e = ET.Element(t('Month'))
        month_e.text = month

        recpattern.add_child(dow_e)
        recpattern.add_child(weekindex_e)
        recpattern.add_child(month_e)

    else:
        recpattern = CNode(name='AbsoluteYearlyRecurrence')

        dtstart = event_start

        monthday = dtstart.day
        monthday_e = CNode(name='DayOfMonth', content=str(monthday))

        month_e = dt2ex_month(event_start)
        
        recpattern.add_child(monthday_e)
        recpattern.add_child(month_e)

    return recpattern

def daily_recpattern2rrule(recurrence, rules):
    rules['freq'] = 'DAILY'
    rules['interval'] = recurrence.get('t:Interval')

def weekly_recpattern2rrule(recurrence, rules):
    dow = recurrence.get('t:DaysOfWeek').split()
    rules['interval'] = recurrence.get('t:Interval')

    rules['freq'] = 'DAILY'
    byday_rules = [weekday_xml2ical(w) for w in dow]
    rules['byday'] = byday_rules

def rel_monthly_recpattern2rrule(recurrence, rules):
    rules['interval'] = recurrence.get('t:Interval')

    dow = recurrence.get('t:DaysOfWeek').split()
    dow = [weekday_xml2ical(w) for w in dow]

    dow_index = recurrence.get('t:DayOfWeekIndex')
    if dow_index == 'Last':
        cal_idx = -1
    else:
        wks = ['', 'First', 'Second', 'Third', 'Fourth']
        cal_idx = wks.index(dow_index)

    byday_rules = ["%s%s" %(str(cal_idx), wd) for wd in dow]

    rules['freq'] = 'MONTHLY'
    rules['BYDAY'] = byday_rules

def abs_monthly_recpattern2rrule(recurrence, rules):
    rules['interval'] = recurrence.get('t:Interval')
    rules['freq'] = 'MONTHLY'
    rules['bymonthday'] = recurrence.get('t:DayOfMonth')

def rel_yearly_recpattern2rrule(recurrence, rules):
    rules['freq'] = 'YEARLY'
    dow = recurrence.get('t:DaysOfWeek')
    windex = recurrence.get('t:DayOfWeekIndex')
    month = recurrence.get('t:Month')

    byday, bymonth = rel_year2bday(dow, windex, month)
    rules['byday'] = byday
    rules['bymonth'] = bymonth
    rules['interval'] = 1 # Fixed by Exchange

def abs_yearly_recpattern2rrule(recurrence, rules):
    rules['freq'] = 'YEARLY'
    rules['bymonthday'] = recurrence.get('t:DayOfMonth')
    rules['bymonth'] = ex_month2monthno(recurrence.get('t:Month'))
    rules['interval'] = 1 # Fixed by Exchange

def byday2rel_month(byday):
    """Convert a BYDAY recurrence rule to Exchange rules.
    returns equivalent (DaysOfWeek, DayOfWeekIndex) Exchange rules
    """
    m = re.match('([+-])?(\d)(\w+)$', byday)
    sign, wnum, wday = m.groups()
    wnum = int(wnum)

    # TODO: sign == -1 and wnum != 1 isn't possible on
    # exchange. how do we handle that?
    if sign == "-" and wnum == 1:
        weekindex = 'Last'
    else:
        weekindex = ['First', 'Second', 'Third', 'Fourth'][wnum-1]

    wday = weekday_ical2xml(wday)

    dow_e = CNode(name='DaysOfWeek',content=wday)
    weekindex_e = CNode(name='DayOfWeekIndex',content=weekindex)

    return (dow_e, weekindex_e)

def rel_year2bday(dow, weekindex, month):
    """Converts daysofweek, weekindex and month to iCalendar format.

    rel_month2byday('Monday', 'First', 'January')
        => (['1MO'], 1)

    """
    ical_dow = [weekday_xml2ical(w) for w in dow.split()]
    
    if weekindex == 'Last':
        cal_idx = -1
    else:
        wks = ['', 'First', 'Second', 'Third', 'Fourth']
        cal_idx = wks.index(weekindex)

    byday_rules = ["%s%s" %(str(cal_idx), r) for r in ical_dow]

    ical_month = ex_month2monthno(month)

    return (byday_rules, ical_month)

    
ex_months = ["", "January", "February", "March", "April", "May",
             "June", "July", "August", "September", "October",
             "November", "December"]

def dt2ex_month(dt):
    """Convert a xs:dateTime to a month name for Exchange"""
    month_e = CNode(name='Month', content=ex_months[dt.month])
    return month_e

def ex_month2monthno(month):
    return ex_months.index(month)



def to_start_element(dt):
    e = ET.Element(t('Time'))
    e.text = "%02d:%02d:%02d" %(dt.hour, dt.minute, dt.second)
    return e


def vtimezone2ex_timezone(vtz):
    """Convert an iCalendar timezone to TimeZoneType"""
    f = open('/tmp/debug.txt', 'a')
    f.write('converting timezone: \n')

    # Standard MUST be specified, according to the standard
    if len(vtz.walk('standard')) > 0:
        standard = vtz.walk('standard')[0]
        # standard offset in hours
        standard_offset = standard['tzoffsetto'].td.seconds / 3600
    else:
        ValueError, "STANDARD time must be specified in a VTIMEZONE"

    # Daylight CAN be specified
    if len(vtz.walk('daylight')) > 0:
        daylight = vtz.walk('daylight')[0]
        # daylight offset in hours
        daylight_offset = daylight['tzoffsetto'].td.seconds / 3600
    else:
        # TODO: return just standard, and make Calendar(/Item)
        # understand it
        daylight = standard

    tz_e = ET.Element(t('MeetingTimeZone'))
    base_offset_e = ET.SubElement(tz_e, t('BaseOffset'))
    base_offset_e.text = 'PT0H'

    # Standard time
    standard_e = ET.SubElement(tz_e, t('Standard'))
    offset_e = ET.SubElement(standard_e, t('Offset'))
    offset_e.text = "PT%dH" % standard_offset
    standard_e.append(rrule2yearly_recpattern(standard['rrule'],1))
    standard_time_e = to_start_element(standard['dtstart'].dt)
    standard_e.append(standard_time_e)

    # Daylight saving time
    daylight_e = ET.SubElement(tz_e, t('Daylight'))
    offset_e = ET.SubElement(daylight_e, t('Offset'))
    offset_e.text = "PT%dH" % daylight_offset
    daylight_e.append(rrule2yearly_recpattern(daylight['rrule'],1))
    daylight_time_e = to_start_element(daylight['dtstart'].dt)
    daylight_e.append(daylight_time_e)

    f.write('\n\n')

    f.write(ET.tostring(tz_e))

    return tz_e

def ex_timezone2vtimezone(ex_tz):
    """Convert TimeZoneType to VTIMEZONE"""
    of_e = ex_tz.find(t('BaseOffset'))
    base_offset = xs_duration2timedelta(of_e)
    # std_recur = - recursion :<
    return None
