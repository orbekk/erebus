from CalendarVisitor import *

from xml.etree import *
from helper.id import *
from helper.timeconv import *
from helper.icalconv import *

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

        def conv(ical_e, xml_e, f):
            xml_v = ci.get(xml_e)
            if not xml_v: return
            print "xml:", xml_v
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

        if ci.get('t:Body') != None:
            self.set('t:Body:BodyType', 'Text')

        return e
