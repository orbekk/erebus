from CalendarVisitor import *

from xml.etree import *
from helper.id import *
from helper.timeconv import *
from helper.icalconv import *
from helper.recurrence import *

import datetime
import icalendar as ical
from icalendar import Calendar as ICal
from icalendar import Event

class GenerateICalVisitor(CalendarVisitor):
    def __init__(self):
        self.ical = ICal()
        self.ical.add('prodid', '-//Erebus//hig.no//')
        self.ical.add('version', '2.0')

    def visitCalendar(self, calendar):
        calendaritems = self.accept(calendar, 'calendaritems')
        for c in calendaritems:
            self.ical.add_component(c)

        return self.ical

    def visitCalendarItem(self, ci):
        e = Event()

        def conv(xml_e, ical_e, f):
            xml_v = ci.get(xml_e)
            if not xml_v: return
            ical_v = f(xml_v)
            if not ical_v: return

            e.add(ical_e, ical_v)

        conv('t:Subject', 'summary', identity)
        conv('t:Start', 'dtstart', xsdt2datetime)
        conv('t:End', 'dtend', xsdt2datetime)
        conv('t:Sensitivity', 'class', sensitivity2class)
        conv('t:Location', 'location', identity)
        conv('t:DateTimeCreated', 'dtstamp', xsdt2datetime)
        conv('t:Body', 'description', identity)

        rrule = self.accept1(ci, 'recurrence')
        if rrule != None:
            e.add('rrule', rrule)

        tz = self.accept1(ci, 'timezone')

        if ci.get('t:Body') != None:
            self.set('t:Body:BodyType', 'Text')

        return e

    def visitRecurrence(self, rec):
        children = rec.et.getchildren()
        rec_pattern = children[0]
        rec_range = children[1]
        
        rrule = {}
        rec_type = no_namespace(rec_pattern.tag)

        if  rec_type == 'DailyRecurrence':
            daily_recpattern2rrule(rec, rrule)
        elif rec_type == 'WeeklyRecurrence':
            weekly_recpattern2rrule(rec, rrule)
        elif rec_type == 'RelativeMonthlyRecurrence':
            rel_monthly_recpattern2rrule(rec, rrule)
        elif rec_type == 'AbsoluteMonthlyRecurrence':
            abs_monthly_recpattern2rrule(rec, rrule)
        elif rec_type == 'RelativeYearlyRecurrence':
            rel_yearly_recpattern2rrule(rec, rrule)
        elif rec_type == 'AbsoluteYearlyRecurrence':
            abs_yearly_recpattern2rrule(rec, rrule)
        else:
            raise ValueError("unknown recurrence pattern: %s" % rec_type)
    

        range_type = no_namespace(rec_range.tag)
        if range_type == 'NumberedRecurrence':
            count = rec.get('t:NumberOfOccurrences')
            rrule['COUNT'] = count
        elif range_type == 'EndDateRecurrence':
            enddate = rec.get('t:EndDate')
            rrule['UNTIL'] = xs_date2datetime(enddate)
        else:
            # NoEndRecurrence is the default in iCalendar
            pass


        return rrule

    def visitTimeZone(self, tz):

        base_offset = xs_duration2timedelta(tz.get('t:BaseOffset'))
        recurrences = self.accept(tz, 'recurrence')

        print "got base_offset", base_offset

        tz = ical.Timezone()
         
        if len(recurrences) == 0:
            std = ical.cal.Component()
            std.name = 'STANDARD'
            std.add('tzoffsetfrom', datetime.timedelta(0))
            std.add('tzoffsetto', base_offset)
            tz.add_component(std)

            print tz.as_string()

            #std.add
        elif len(recurrences) == 1:
            pass
        elif len(recurrences) == 2:
            pass

        return 
           
