from xml.etree import ElementTree as ET
from helper.timeconv import *
from namespaces import *
import re

def rrule2yearly_recpattern(rrule,interval_e):
    """Convert a YEARLY iCalendar recurrence to Exchange's
    RecurrencePattern

    rrule: the iCalendar recurrence rule
    interval_e: the interval element
    """
    if rrule.has_key('byday') and rrule.has_key('bymonth'):
        reqpattern = ET.Element(t('RelativeYearlyRecurrence'))

        dow_e, weekindex_e = byday2rel_month(rrule['byday'][0])
        month_e = xsdt2ex_month(self.get('t:Start'))

        # reqpattern.append(interval_e) # Exchange doesn't support
        # this in yearly recurrences
        reqpattern.append(dow_e)
        reqpattern.append(weekindex_e)
        reqpattern.append(month_e)

    else:
        reqpattern = ET.Element(t('AbsoluteYearlyRecurrence'))

        dtstart = xsdt2datetime(self.get('t:Start'))

        monthday = dtstart.day
        monthday_e = ET.Element(t('DayOfMonth'))
        monthday_e.text = str(monthday)

        month_e = xsdt2ex_month(self.get('t:Start'))
        
        reqpattern.append(monthday_e)
        reqpattern.append(month_e)

    return reqpattern

def byday2rel_month(byday):
    """Convert a BYDAY recurrence rule to Exchange rules.
    returns equivalent (DaysOfWeek, DayOfWeekIndex) Exchange rules
    """
    reqpattern = ET.Element(t('RelativeMonthlyRecurrence'))
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

    dow_e = ET.Element(t('DaysOfWeek'))
    dow_e.text = wday

    weekindex_e = ET.Element(t('DayOfWeekIndex'))
    weekindex_e.text = weekindex

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

def xsdt2ex_month(xsdt):
    """Convert a xs:dateTime to a month name for Exchange"""
    dt = xsdt2datetime(xsdt)
    month_e = ET.Element(t('Month'))
    month_e.text = ex_months[dt.month]

    return month_e

def ex_month2monthno(month):
    return ex_months.index(month)
