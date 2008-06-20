# -*- coding: utf-8 -*-
from xml.etree import ElementTree as ET
from helper.etsearch import elementsearch
from helper.timeconv import *
from helper.id import identity
from namespaces import *
from Queue import Queue
from icalendar import Event
from icalendar import Calendar as ICal
from datetime import datetime
from helper.icalconv import *
from string import join
from helper.recurrence import *
import re
import copy

from exchangetypes.ExchangeItem import ExchangeItem

class CalendarItem(ExchangeItem):

    @staticmethod
    def from_ical(ical):
        item = CalendarItem(ET.Element(t('CalendarItem')))
        item._from_ical(ical)
        return item

    def __init__(self, et):
        ExchangeItem.__init__(self,et)
        self.get_attrs()
        self.icalClass = Event
        
        self.trans_xml2ical = \
        [  # See ExchangeItem.to_ical
            ('t:Subject',         'summary',     identity),
            ('t:Start',           'dtstart',     xsdt2datetime),
            ('t:End',             'dtend'  ,     xsdt2datetime),
            ('t:Sensitivity',     'class',       sensitivity2class),
            ('t:Location',        'location',    identity),
            ('t:DateTimeCreated', 'dtstamp',     xsdt2datetime),
            ('t:Body',            'description', identity)
        ]

        self.trans_ical2xml = \
        [
            ('summary',     't:Subject',         identity),
            ('class',       't:Sensitivity',     class2sensitivity),
            ('description', 't:Body',            identity),
            ('dtstart',     't:Start',           ical2xsdt),
            ('dtend',       't:End',             ical2xsdt),
            ('location',    't:Location',        identity),
#            ('dtstamp', 't:DateTimeCreated', ical2xsdt),
        ]    

    def is_exchangeItem(self):
        """
        This is a exchange item if ItemId:Id is set
        """
        itemid = self.get('t:ItemId:Id')
        return (itemid != None and itemid != '')

    def get_attrs(self):
        et = self.et
        if et.tag != t('CalendarItem'):
            raise Exception("Invalid item: %s, expected %s" %(et.tag, 'CalendarItem'))

    def _from_ical(self, ical):
        # Handle UID, two cases
        self.uid = ical['uid']

        # Add this to the natural position in the tree
        self.set('t:ItemId:Id', '') 

        ####
        # ID handling
        m = re.search('([^.]*)\.([^@]*)@hig\.no', self.uid)
        if m:
            # Case 1, items made in exchange will have the
            # id.chkey@hig.no uid
            ex_id, ex_chkey = m.groups()
            self.set('t:ItemId:Id', ex_id)
            self.set('t:ItemId:ChangeKey', ex_chkey)
        else:
            # Case 2, convert with icalconv
            exchange_id = getExchangeId(self.uid)
            if exchange_id:
                ex_id, ex_chkey = exchange_id
                self.set('t:ItemId:Id', ex_id)
                self.set('t:ItemId:ChangeKey', ex_chkey)

        super(CalendarItem, self)._from_ical(ical)

        if self.get('t:Body') != None:
            self.set('t:Body:BodyType', 'Text')


        ####
        # Recurrence handling
        fi = open('/tmp/recurrence.log', 'a')
        fi.write('checking for recurrence\n')
        
        def rrule2recurrence(rrule):

            # Find interval (or default to 1)
            if rrule.has_key('INTERVAL'):
                interval = rrule['INTERVAL'][0]
            else:
                interval = 1
            interval_e = ET.Element(t('Interval'))
            interval_e.text = str(interval)

            has_recurrence = False
            recurrence = ET.Element(t('Recurrence'))

            fi.write("rrule: "+str(rrule)+"\n\n")

            freq = rrule['FREQ'][0]


            if freq == 'YEARLY':
                if rrule.has_key('byday') and rrule.has_key('bymonth'):
                    reqpattern = ET.Element(t('RelativeYearlyRecurrence'))

                    dow_e, weekindex_e = byday2rel_month(rrule['byday'][0])
                    month_e = xsdt2ex_month(self.get('t:Start'))

                    reqpattern.append(interval_e)
                    reqpattern.append(dow_e)
                    reqpattern.append(weekindex_e)
                    reqpattern.append(month_e)

                    recurrence.append(reqpattern)

                else:
                    reqpattern = ET.Element(t('AbsoluteYearlyRecurrence'))

                    dtstart = xsdt2datetime(self.get('t:Start'))

                    monthday = dtstart.day
                    monthday_e = ET.Element(t('DayOfMonth'))
                    monthday_e.text = str(monthday)

                    month_e = xsdt2ex_month(self.get('t:Start'))
                    
                    reqpattern.append(monthday_e)
                    reqpattern.append(month_e)

                    recurrence.append(reqpattern)

            elif freq == 'MONTHLY' and rrule.has_key('BYDAY'):
                # When more than one day, it is impossible to do in
                # Exchange (except if all days are in the same week)
                day = rrule['byday'][0] # for day in rrule['byday']:

                reqpattern = ET.Element(t('RelativeMonthlyRecurrence'))
                dow_e, weekindex_e = byday2rel_month(day)

                reqpattern.append(dow_e)
                reqpattern.append(weekindex_e)

                recurrence.append(reqpattern)

                
            elif freq == 'WEEKLY' or \
               (freq == 'DAILY' and rrule.has_key('BYDAY')):
                                    
                has_recurrence = True
                reqpattern = ET.Element(t('WeeklyRecurrence'))

                daysofweek = ET.Element(t('DaysOfWeek'))
                
                if rrule.has_key('WKST') or rrule.has_key('BYDAY'):
                    if rrule.has_key('WKST'): # TODO: really?
                        ical_days = rrule['WKST']
                    else:
                        ical_days = rrule['BYDAY']
                    
                    days = [weekday_ical2xml(w) for w in ical_days]
                    daysofweek.text = " ".join(days)

                else:
                    tt = xsdt2datetime(self.get('t:Start'))
                    wkday = dt2xml_weekday(tt)
                    daysofweek.text = wkday

                reqpattern.append(interval_e)
                reqpattern.append(daysofweek)

                recurrence.append(reqpattern)

            elif freq == 'MONTHLY':
                reqpattern = ET.Element(t('AbsoluteMonthlyRecurrence'))
                reqpattern.append(interval_e)

                if rrule.has_key('BYMONTHDAY'):
                    mday = str(rrule['BYMONTHDAY'][0])
                else:
                    dt = xsdt2datetime(self.get('t:Start'))
                    mday = str(dt.day)

                dayofmonth = ET.Element(t('DayOfMonth'))
                dayofmonth.text = mday
                
                reqpattern.append(dayofmonth)
                recurrence.append(reqpattern)
                
            elif freq == 'DAILY':
                reqpattern = ET.Element(t('DailyRecurrence'))
                reqpattern.append(interval_e)

                recurrence.append(reqpattern)

            startdate = ET.Element(t('StartDate')) # User start date
            startdate.text = xs_dateTime2xs_date(self.get('t:Start'))

            if rrule.has_key('count'):
                reqrange = ET.Element(t('NumberedRecurrence'))

                count_e = ET.Element(t('NumberOfOccurences'))
                count_e.text = rrule['count']

                reqrange.append(startdate)
                reqrange.append(count_e)

            elif rrule.has_key('until'):
                reqrange = ET.Element(t('EndDateRecurrence'))

                enddate = ical2xsdt(rrule['until'])
                enddate = xs_dateTime2xs_date
                enddate_e = ET.Element(t('EndDate'))
                enddate_e.text = enddate

                reqrange.append(startdate)
                reqrange.append(enddate_e)

            else:
                noend     = ET.Element(t('NoEndRecurrence'))
                noend.append(startdate)
            
                recurrence.append(noend)

            return recurrence
                    

        if ical.has_key('rrule'):
            fi.write("ical has rrule!\n")
            fi.write(ical.as_string())
            recurrence = rrule2recurrence(ical['rrule'])
            if recurrence != None:
                self.et.append(recurrence)

        fi.write("Exchange item:\n%s\n\n" % ET.tostring(self.et))
            
        # debug
        # f = open("/tmp/item_from_ical.xml", "w")
        # f.write(ET.tostring(self.et))
        # f.close()

    def to_ical(self):
        e = ExchangeItem.to_ical(self)

        if self.get('t:ItemId:Id') and self.get('t:ItemId:ChangeKey'):
            e['uid'] = "%s.%s@hig.no" %(self.get("t:ItemId:Id"),
                                        self.get("t:ItemId:ChangeKey"))


        # Handle recurrence
        rec = self.recurrence_exch2ical()
        if rec: e.add('rrule', rec)

        return e

    def recurrence_exch2ical(self):
        fi = open('/tmp/recurrence.log', 'a')
        fi.write('checking for recurrence\n')

        def recurrence2rrule(item):
            cs = item.getchildren()
            rec_pattern = cs[0]
            rec_range   = cs[1]
            rrule = {}

            rec_ptag  = no_namespace(rec_pattern.tag)
            rec_table = {
                'DailyRecurrence'           : 'DAILY',
                'WeeklyRecurrence'          : 'WEEKLY',
                'RelativeMonthlyRecurrence' : 'MONTHLY',
                'AbsoluteMonthlyRecurrence' : 'MONTHLY',
                'RelativeYearlyRecurrence'  : 'YEARLY',
                'AbsoluteYearlyRecurrence'  : 'YEARLY',
                }

            freq = rec_table[rec_ptag]

            interval = rec_pattern.find(t('Interval'))
            if interval != None:
                interval = interval.text
            else:
                interval = '1'

            if freq != 'YEARLY':
                rrule['INTERVAL'] = interval

            # Check DaysOfWeek
            byday_rules = []
            dow = self.get('t:DaysOfWeek')
            if dow:
                ical_dow = [weekday_xml2ical(w) for w in dow.split()]

                for w in ical_dow:
                    byday_rules.append(w)

#                 if freq == 'WEEKLY' and len(ical_dow) > 1:
#                     freq = 'DAILY'

            if self.get('t:DayOfWeekIndex') != None:
                weekindex = self.get('t:DayOfWeekIndex')
                if weekindex == 'Last':
                    cal_idx = -1
                else:
                    wks = ['', 'First', 'Second', 'Third', 'Fourth']
                    cal_idx = wks.index(weekindex)
                byday_rules = ["%s%s" %(str(cal_idx), r) for r in byday_rules]

            if self.get('t:DayOfMonth') != None:
                dayofmonth = self.get('t:DayOfMonth')
                rrule['BYMONTHDAY'] = dayofmonth

            if byday_rules != []:
                rrule['BYDAY'] = byday_rules


            range_type = no_namespace(rec_range.tag)
            if range_type == 'NumberedRecurrence':
                count = rec_range.find(t('NumberOfOccurences')).text
                rrule['COUNT'] = count
            elif range_type == 'EndDateRecurrence':
                enddate = rec_range.find(t('EndDate'))
                rrule['UNTIL'] = xs_date2datetime(enddate)
            else:
                # NoEndRecurrence is the default in iCalendar
                pass
                
            rrule['FREQ'] = freq
            return rrule

        
        recur = self.get('t:IsRecurring')
        if recur == 'true':
            fi.write('Item is recurring, TODO: get RecurringMaster\n')

        recur = self.get('t:CalendarItemType')
        if recur == 'RecurringMaster' or self.get_item('t:Recurrence'):
            fi.write('Item is RecurringMaster. TODO: magic!\n')
            fi.write(ET.tostring(self.get_item('t:Recurrence')) + "\n")
            rec = recurrence2rrule(self.get_item('t:Recurrence'))
            fi.write("Got recurrence: %s\n\n" % rec)
            return rec
        
        return None


    def get_new_exchangeitem(self, uid_ignore, allItems):
        """Return this item (as XML), but:
        
        - If the item is in uid_ignore, return None
        - If the item has an Exchange id, return None
        """
        
        if allItems == False:
            if self.is_exchangeItem() or uid_ignore.has_key(self.uid):
                return None

        # We just need to delete the empty ItemId node:
        ex_tree = copy.deepcopy(self.et)
        ex_tree.remove(ex_tree.find(t('ItemId')))

        uid_ignore[self.uid] = True
        
        return ex_tree
            
            
