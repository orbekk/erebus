from CalendarVisitor import *

from xml.etree import *
from helper.id import *
from helper.timeconv import *
from helper.icalconv import *
from helper.recurrence import *

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

        rrule = self.accept(ci, 'recurrence')
        if len(rrule) > 0:
            rrule = rrule[0]
        if rrule != None:
            e.add('rrule', rrule)

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
    

        return rrule
