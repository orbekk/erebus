from Visitor.CNodeVisitor import *
from CNode import *
from namespaces import *
from helper.id import identity
from helper.icalconv import *
from helper.timeconv import *
from helper.recurrence import *

class Erebus2ICSVisitor(CNodeVisitor):

    def __init__(self,cnode):
        self.ebus = cnode

    def run(self):
        self.cal = CNode('vcalendar')
        
        self.cal.attr['prodid'] = '-//Erebus//hig.no//'
        self.cal.attr['version'] = '2.0'

        for e in self.accept(self.ebus, 'event'):
            self.cal.add_child(e)

        return self.cal

    def visit_event(self,cnode):
        e = CNode('vevent')

        def conv(ebus, icaln, f):
            if not cnode.attr.has_key(ebus): return
            ebus_v = cnode.attr[ebus]
            new = f(ebus_v)
            #if not new: return

            e.attr[icaln] = new

        conv('summary', 'summary', identity)
        conv('start', 'dtstart', dt2vDDD)
        conv('end', 'dtend', dt2vDDD)
        conv('class', 'class', identity)
        conv('location', 'location', identity)
        conv('timestamp', 'dtstamp', dt2vDDD)
        conv('description', 'description', identity)

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
