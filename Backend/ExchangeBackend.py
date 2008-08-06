# -*- coding: utf-8 -*-
from Backend import Backend
from CNode import *
from Visitor.EWS2ErebusVisitor import *
from Visitor.Erebus2EWSVisitor import *
from Visitor.Erebus2EWSUpdate import *
from Visitor.ToStringVisitor import *

from xml.etree import ElementTree as ET
from erebusconv import xml2cnode, cnode2xml

from namespaces import *
from soapquery import *
import os
import sys

class ExchangeBackend(Backend):
    proplist = ['item:Subject',
                'calendar:Start',
                'calendar:End',
                'calendar:IsAllDayEvent',
                'calendar:Location',
                'calendar:MeetingTimeZone',
                'calendar:Recurrence',
                'item:Sensitivity',
                'item:DateTimeCreated',
                'item:Body']
    
    def __init__(self,host,user=None,password=None,https=False,auth=None):
        """Initialises the backend

        host: the hostname to the Exchange server
        auth: is the authorisation string for basic authorisation (may
              be specified instead of user/pass)
        """
        Backend.__init__(self)
        self.conn = SoapConn(host,https=https,user=user,password=password,
                             auth=auth)
        self.query = SoapQuery(self.conn)


    def __conv(self,string):
        return xml2cnode(ET.XML(string))

    def get_item(self,id):
        if id.name == 'exchange_id':
            itemid = id.attr['id']
            if id.attr.has_key('changekey'):
                changekey = id.attr['changekey']
            else:
                changekey = None
        else:
            raise ValueError("Unknown item %s" % str(id))

        item = self.query.get_item((itemid, changekey), extra_props=['item:Body'])
        ctree = self.__conv(item)
        return EWS2ErebusVisitor(ctree).run()

    def get_all_items(self):
        items = self.query.get_all_calendar_items(extra_props=self.proplist)
        ctree = self.__conv(items)
        # print ToStringVisitor().visit(ctree)
        
        return EWS2ErebusVisitor(ctree).run()

    def get_all_item_ids(self):
        items = self.query.find_items('calendar', baseshape='IdOnly')
        ctree = self.__conv(items)
        return EWS2ErebusVisitor(ctree).run()

    def delete_item(self,id):
        """Delete one or more items

        Searches for exchange_ids in `id' and deletes all occurences.
        """
        exchange_ids = id.search('exchange_id', all=True)

        itemids = []
        for e in exchange_ids:
            itemid = e.attr['id']
            chkey = e.attr['changekey']
            itemids.append((itemid,chkey))
                
        if len(itemids) > 0:
            self.query.delete_items(itemids)
        

    def delete_all_items(self):
        self.delete_item(self.get_all_item_ids())

    def create_item(self, item):
        if not item.search('event'):
            return

        ewsitem = Erebus2EWSVisitor(item).run()
        xml = cnode2xml(ewsitem)

        print ToStringVisitor(with_types=True).visit(ewsitem)
        tmpnam= os.tmpnam() + '.xml'
        print "Writing query to " + tmpnam
        f = open(tmpnam,'w')
        f.write(ET.tostring(xml))
        f.close()

        res = self.query.create_items(ET.tostring(xml))
        cn = xml2cnode(ET.XML(res))
        StripNamespaceVisitor().visit(cn)

        eid = CNode('exchange_id')
        itemid = cn.search('ItemId')
        eid.attr['id'] = itemid.attr['Id']
        eid.attr['changekey'] = itemid.attr['ChangeKey']

        return eid


    def update_item(self, id, item_changes):
        """Update an item with the fields from item_changes"""

        if id.name == 'exchange_id':
            itemid = id.attr['id']
            if id.attr.has_key('changekey'):
                changekey = id.attr['changekey']
            else:
                changekey = None
        else:
            raise ValueError("Unknown item %s" % str(id))

        ewsitem = Erebus2EWSUpdate(item_changes).run()
        xmlitem = cnode2xml(ewsitem)
        xmlitem = ET.tostring(xmlitem)

        up = self.query.update_item(itemid, changekey, xmlitem)
        return up
