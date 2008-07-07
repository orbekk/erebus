from Visitor.CNodeVisitor import *
from CNode import *
from namespaces import *
from helper.id import identity
from helper.icalconv import *
from helper.timeconv import *
from helper.recurrence import *
from datetime import datetime, timedelta

from Visitor.ToStringVisitor import *

class Erebus2ICSVisitor(CNodeVisitor):

    def __init__(self,cnode):
        self.ebus = cnode


    def run(self):
        self.cal = CNode('vcalendar')
        
        self.cal.attr['prodid'] = '-//Erebus//hig.no//'
        self.cal.attr['version'] = '2.0'

        for tz in self.accept(self.ebus, 'TimeZone'):
            self.cal.add_child(tz)

        for e in self.accept(self.ebus, 'event'):
            self.cal.add_child(e)

        return self.cal

    def __pack_recurrence(self,rec_element):
        rec = CNode('Recurrence')
        rec.add_child(rec_element)
        rec.add_child(CNode('NoEndRecurrence'))

        return rec

    def __convert_timezone(self,e_tz,name,base_offset):

        tz_e = CNode(name)
        offset_str = e_tz.search('Offset').content
        offset = (- vDDDTypes.from_ical(offset_str)) + base_offset
        tz_e.attr['tzoffsetto'] = offset

        _time = xs_time2time(e_tz.search('Time').content)
        dt = datetime(1970, 1, 1, _time.hour, _time.minute, _time.second)
        tz_e.attr['dtstart'] = dt

        rec = e_tz.children[1]
        if "Recurrence" in rec.name:
            rec = self.visit(self.__pack_recurrence(rec))
            tz_e.attr['rrule'] = rec.attr['rrule']
        else:
            raise ValueError("Did not find recurrence element in timezone")

        return tz_e


    def visit_TimeZone(self,cnode):
        standard = cnode.search('Standard')
        daylight = cnode.search('Daylight')

        tz_e = CNode('timezone')
        tz_e.attr['tzid'] = cnode.search('tzid').content

        base_offset_str = cnode.search('BaseOffset').content
        # Exchange does some wacky negation of its timezones
        base_offset = (- vDDDTypes.from_ical(base_offset_str))
        
        if not standard and not daylight:
            # Make a timezone with the base offset only (required by
            # the rfc)
            std_e = CNode('standard')
            std_e.attr['tzoffsetfrom'] = base_offset
            std_e.attr['tzoffsetto'] = base_offset
            std_e.attr['dtstart'] = datetime(1970,01,01)
            tz_e.add_child(std_e)

        if standard:
            std_e = self.__convert_timezone(standard,'standard',base_offset)
            tz_e.add_child(std_e)

        if daylight:
            dayl_e = self.__convert_timezone(daylight,'daylight',base_offset)
            tz_e.add_child(dayl_e)

            # Set offsetfrom both ways
            std_e.attr['tzoffsetfrom'] = dayl_e.attr['tzoffsetto']
            dayl_e.attr['tzoffsetfrom'] = std_e.attr['tzoffsetto']
        else:
            std_e.attr['tzoffsetfrom'] = vDDDTypes.from_ical('PT0M')

        return tz_e


    def visit_event(self,cnode):
        e = CNode('vevent')

        def conv(ebus, icaln, f):
            if not cnode.attr.has_key(ebus): return
            ebus_v = cnode.attr[ebus]
            new = f(ebus_v)
            #if not new: return

            e.attr[icaln] = new

        conv('summary', 'summary', identity)
        conv('class', 'class', identity)
        conv('location', 'location', identity)
        conv('description', 'description', identity)

        tzid = cnode.search('tzid')
        if not tzid:
            # just copy
            timeconv = identity
        else:
            def timeconv(dt):
                # (See erebusconv.py)
                c = CNode('exchange_value', content=dt)
                c.attr['tzid'] = tzid.content
                return c
            
        conv('timestamp', 'dtstamp', timeconv)
        conv('start', 'dtstart', timeconv)
        conv('end', 'dtend', timeconv)



        # get uid (if exchange type)
        itemid = cnode.search('exchange_id')
        if itemid:
            e.attr['uid'] = "%s.%s@hig.no" %(itemid.attr['id'],
                                             itemid.attr['changekey'])
            
        rec = cnode.search('Recurrence')
        if rec:
            rrule = self.visit(rec)
            e.attr['rrule'] = rrule.attr['rrule']

        return e


    def visit_Recurrence(self,rec_node):
        rec = CNode('recurrence')

        rec_pattern = rec_node.children[0]
        rec_range = rec_node.children[1]

        rrule = {}
        rec_type = rec_pattern.name

        if  rec_type == 'DailyRecurrence':
            daily_recpattern2rrule(rec_node, rrule)
        elif rec_type == 'WeeklyRecurrence':
            weekly_recpattern2rrule(rec_node, rrule)
        elif rec_type == 'RelativeMonthlyRecurrence':
            rel_monthly_recpattern2rrule(rec_node, rrule)
        elif rec_type == 'AbsoluteMonthlyRecurrence':
            abs_monthly_recpattern2rrule(rec_node, rrule)
        elif rec_type == 'RelativeYearlyRecurrence':
            rel_yearly_recpattern2rrule(rec_node, rrule)
        elif rec_type == 'AbsoluteYearlyRecurrence':
            abs_yearly_recpattern2rrule(rec_node, rrule)
        else:
            raise ValueError("unknown recurrence pattern: %s" % rec_type)

        range_type = rec_range.content
        if range_type == 'NumberedRecurrence':
            count = rec_range.search('NumberOfOccurrences').content
            rrule['COUNT'] = count
        elif range_type == 'EndDateRecurrence':
            enddate = rec_range.search('EndDate').content
            rrule['UNTIL'] = xs_date2datetime(enddate)
        else:
            # NoEndRecurrence is the default in iCalendar
            pass
                
        rec.attr['rrule'] = rrule

        return rec
