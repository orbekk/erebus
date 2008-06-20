def byday2rel_month(byday)l:
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

    return (dow, weekindex_e)
