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
import re
import copy

from exchangetypes.ExchangeItem import ExchangeItem

class CalendarItem(ExchangeItem):

    @staticmethod
    def fromICal(ical):
        item = CalendarItem(ET.Element(t('CalendarItem')))
        item._fromICal(ical)
        return item

    def __init__(self, et):
        ExchangeItem.__init__(self,et)
        self.get_attrs()
        self.icalClass = Event
        
        self.trans_xml2ical = \
        [  # See ExchangeItem.toICal
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

    def _fromICal(self, ical):
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

        super(CalendarItem, self)._fromICal(ical)

        if self.get('t:Body') != None:
            self.set('t:Body:BodyType', 'Text')


        ####
        # Recurrence handling
        fi = open('/tmp/recurrence.log', 'a')
        fi.write('checking for recurrence\n')
        
        def rrule2recurrence(rrule):
            # Check for relative types
            if rrule['FREQ'][0] == 'YEARLY':
                # TODO: Check BYWEEKNO, BYDAY
                pass
            elif rrule['FREQ'][0] == 'MONTHLY':
                # TODO: Check BYWEEKNO, BYDAY
                pass

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
            # Assume absolute types
            if rrule['FREQ'][0] == 'DAILY':
                has_recurrence = True
                reqpattern = ET.Element(t('DailyRecurrence'))
                reqpattern.append(interval_e)

                recurrence.append(reqpattern)

            elif rrule['FREQ'][0] == 'WEEKLY':
                has_recurrence = True
                reqpattern = ET.Element(t('WeeklyRecurrence'))

                if rrule.has_key('WKST'):
                    daysofweek = ET.Element(t('DaysOfWeek'))
                    for w in rrule['WKST']:
                        daysofweek.text += weekday_ical2xml(str(w))
                else: # TODO: Get weekday from python
                    pass
                recpattern.append(interval_e)

                recurrence.append(reqpattern)

            


            noend     = ET.Element(t('NoEndRecurrence'))
            startdate = ET.Element(t('StartDate')) # User start date
            startdate.text = xs_dateTime2xs_date(self.get('t:Start'))
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
        # f = open("/tmp/item_fromICal.xml", "w")
        # f.write(ET.tostring(self.et))
        # f.close()

    def toICal(self):
        e = ExchangeItem.toICal(self)

        e['uid'] = "%s.%s@hig.no" %(self.get("t:ItemId:Id"),
                                    self.get("t:ItemId:ChangeKey"))


        # Handle recurrence
        rec = self.recurrenceFromXML()
        if rec: e.add('rrule', rec)

        return e

    def recurrenceFromXML(self):
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
            rrule['FREQ'] = freq

            # Check for interval
            if freq != 'YEARLY':
                interval = rec_pattern.find(t('Interval'))
                if interval != None:
                    rrule['INTERVAL'] =interval.text

            fi.write("FREQ=%s;INTERVAL=%s\n" %(freq, interval))

            return rrule

        
        recur = self.get('t:IsRecurring')
        if recur == 'true':
            fi.write('Item is recurring, TODO: get RecurringMaster\n')

        recur = self.get('t:CalendarItemType')
        if recur == 'RecurringMaster':
            fi.write('Item is RecurringMaster. TODO: magic!\n')
            rec = recurrence2rrule(self.getItem('t:Recurrence'))
            fi.write("Got recurrence: %s\n\n" % rec)
            return rec
        
        return None


    def toNewExchangeItem(self, uid_ignore, allItems):
        if allItems == False:
            if self.is_exchangeItem() or uid_ignore.has_key(self.uid):
                return None

        # We just need to delete the empty ItemId node:
        ex_tree = copy.deepcopy(self.et)
        ex_tree.remove(ex_tree.find(t('ItemId')))

        uid_ignore[self.uid] = True
        
        return ex_tree
            
            
