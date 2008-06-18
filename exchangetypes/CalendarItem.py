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
            
        # debug
        # f = open("/tmp/item_fromICal.xml", "w")
        # f.write(ET.tostring(self.et))
        # f.close()

    def toICal(self):
        e = ExchangeItem.toICal(self)

        e['uid'] = "%s.%s@hig.no" %(self.get("t:ItemId:Id"),
                                    self.get("t:ItemId:ChangeKey"))

        return e

    def toNewExchangeItem(self, uid_ignore, allItems):
        if allItems == False:
            if self.is_exchangeItem() or uid_ignore.has_key(self.uid):
                return None

        # We just need to delete the empty ItemId node:
        ex_tree = copy.deepcopy(self.et)
        ex_tree.remove(ex_tree.find(t('ItemId')))

        uid_ignore[self.uid] = True
        
        return ex_tree
            
            
