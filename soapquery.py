# -*- coding: utf8 -*-
from xml.etree import ElementTree as ET
from xml.parsers.expat import ExpatError
from helper.etsearch import elementsearch
from namespaces import *
from exchangetypes import Calendar
import httplib
import base64
import re
import os
import sys
from re import *

# workaround for a python bug (ref. soaplib)
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

types    = "http://schemas.microsoft.com/exchange/services/2006/types"
messages = "http://schemas.microsoft.com/exchange/services/2006/messages"

class QueryError(Exception):
    def __init__(self, str, query=None, result=None):
        self.msg = str
        self.query = query
        self.maybe_write(query, 'query')

        self.result = result
        self.maybe_write(result, 'result')

    def maybe_write(self, str, name):
        if str:
            tmpnam = os.tmpnam() + '.xml'
            f = open(tmpnam, 'w')
            f.write(str)
            self.msg += "\n [%s written to %s]" %(name, tmpnam)
            
    def __str__(self):
        return repr(self.msg)

class SoapConn:
    def __init__(self,host,https=False,user=None,password=None,auth=None):
        self.host     = sub('^http://', '', host)
        self.https    = https
        self.user     = user
        self.password = password
        self.headers  = \
        {
         "Content-Type"   : 'text/xml; charset="utf-8"',
         "Accept"         :
         'application/soap+xml, application/dime, multipart/related, text/*',
         "User-Agent"     : 'MySoap/0.1',
         }

        if auth:
            self.auth = auth
        elif (self.user and self.password):
            auth = base64.b64encode("%s:%s" %(self.user, self.password))
            self.auth = ("Authorization", "Basic %s" % auth)
        

    def make_connection(self):
        if self.https:
            conn = httplib.HTTPSConnection(self.host)
        else:
            conn = httplib.HTTPConnection(self.host)

        if self.auth:
            self.headers[self.auth[0]] = self.auth[1]

        return conn

    def do_query(self,path,query,action,extra_headers=[]):
        headers = self.headers

        headers["SOAPAction"] = action
        headers["Content-Length"] = len(query)


        for k,v in extra_headers:
            headers[k] = v

        conn = self.make_connection()
        conn.request("POST", path, body=query, headers=headers)

        res  = conn.getresponse()
        data = res.read()

        if str(res.status) not in ['200', '202']:
            raise QueryError('Error: %s\n %s\n /tmp/error.xml'%(res.status,
                                                               res.reason),
                            query=query, result=data)

        return data

def soapmethod(f):
    def new(self, *args, **kws):
        xml = ET.XML(f(self, *args, **kws))
        body = elementsearch(xml, "{http://schemas.xmlsoap.org/soap/envelope}Body")

        if body == None:
            raise ValueError("Could not find <soap:Body/> element")

        soap_action = body.getchildren()[0].tag

        return self.soapconn.do_query("/ews/Exchange.asmx",f(*args,**kws),soap_action)


class SoapQuery:

    def msquery(self,string,header=""):
        header += '<t:RequestServerVersion Version="Exchange2007_SP1"/>'
        query = \
"""<?xml version="1.0" encoding="utf-8"?>
 <soap:Envelope
   xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
   xmlns="%s" xmlns:t="%s">
   <soap:Header>%s</soap:Header>
     <soap:Body>
       %s
     </soap:Body>
   </soap:Envelope>""" %(messages, types, header, string)

        # Handy for debugging last request
        f = open('/tmp/lastquery.xml', 'a')
        f.write("\n\n\n"+query)
        f.close()

        try:
            xml = ET.XML(query)
        except ExpatError:
            e = sys.exc_value
            raise QueryError(str(e), query=query)
            
        body = elementsearch(xml, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
        if body == None:
            raise QueryError("Could not find soap:Body element", query=query)

        soap_action = body.getchildren()[0].tag
        soap_action = re.sub('{', '', soap_action)
        soap_action = re.sub('}', '/', soap_action)
        
        return self.soapconn.do_query("/ews/Exchange.asmx",query,soap_action)
        

    def __init__(self,soapconn):
        self.soapconn = soapconn

    
    def get_folder(self,foldername):
        return self.msquery("""
<GetFolder>
  <FolderShape>
    <t:BaseShape>AllProperties</t:BaseShape>
  </FolderShape>
  <FolderIds>
    <t:DistinguishedFolderId Id=\"%s\"/>
  </FolderIds>
</GetFolder>
""" % foldername)


    def find_items(self,parent_folder,baseshape="AllProperties",extra_props=[]):
        props = ""
        for p in extra_props:
            props += "<t:FieldURI FieldURI=\"%s\"/>" % p

        if props != "":
            props = """
<t:AdditionalProperties>
  %s
</t:AdditionalProperties>""" % props


        return self.msquery("""
<FindItem Traversal="Shallow">
  <ItemShape>
    <t:BaseShape>%s</t:BaseShape>
    %s
  </ItemShape>
  <ParentFolderIds>
    <t:DistinguishedFolderId Id="%s"/>
  </ParentFolderIds>
</FindItem>
""" % (baseshape, props, parent_folder))


    def delete_items(self,itemids,delete_type="MoveToDeletedItems",
                   send_cancellations="SendToNone"):
        """
        delete_type: {HardDelete, SoftDelete, *MoveToDeletedItems*}
        send_cancellations: {*SendToNone*, SendOnlyToAll, SendToAllAndSaveCopy}
        """

        ids = ""
        if type(itemids) == list:
            for itemid,chkey in itemids:
                ids += """<t:ItemId Id="%s" ChangeKey="%s"/>""" %(itemid,chkey)
        else:
            ids = """<t:ItemId Id="%s" ChangeKey="%s"/>""" % itemids
        
        return self.msquery("""
<DeleteItem DeleteType="%s"
            SendMeetingCancellations="%s">
  <ItemIds>
    %s
  </ItemIds>
</DeleteItem>
""" %(delete_type, send_cancellations, ids))

    def create_item(self,calendar_items,send_invitations="SendToNone"):
        """
        send_cancellations: {*SendToNone*, SendOnlyToAll, SendToAllAndSaveCopy}
        """

        return self.msquery("""
<CreateItem SendMeetingInvitations="%s">
  <Items>
    %s
  </Items>      
</CreateItem>
"""%(send_invitations,
     calendar_items))


    def get_item(self, itemids, shape="AllProperties",
                extra_props=""):
        """
        Get an item
        """
        props = ""
        for p in extra_props:
            props += "<t:FieldURI FieldURI=\"%s\"/>" % p

        if props != "":
            props = """
<t:AdditionalProperties>
  %s
</t:AdditionalProperties>""" % props

        ids = ""
        if type(itemids) == list:
            for itemid,chkey in itemids:
                ids += """<t:ItemId Id="%s" ChangeKey="%s"/>""" %(itemid,chkey)
        else:
            ids = """<t:ItemId Id="%s" ChangeKey="%s"/>""" % itemids
        
        
        return self.msquery("""
<GetItem>
  <ItemShape>
    <t:BaseShape>%s</t:BaseShape>
    %s
  </ItemShape>
  <ItemIds>
  %s
  </ItemIds>
</GetItem>
""" %(shape,props,ids))


    def get_all_calendar_items(self):
        """
        Return all items with all needed properties
        """
        r = ET.XML(self.find_items('calendar', baseshape="IdOnly"))
        id_elems = elementsearch(r, t('ItemId'), all=True)
        item_ids = [(i.attrib['Id'], i.attrib['ChangeKey']) for i in id_elems]
        if len(item_ids) == 0: return "<Items></Items>"

        return self.get_item(item_ids, extra_props=['item:Body'])


    def get_attachment(self, ids):
        if not type(ids) == list:
            ids = [ids]

        itemids = ""
        for i in ids:
            itemids += '<t:AttachmentId Id="%s"/>' % i

        return self.msquery("""
<GetAttachment>
  <AttachmentIds>
  %s
  </AttachmentIds>
</GetAttachment>
""" % itemids)


    def get_named_attachment(self, itemid, name):
        """
        Return the attachment with name `name'
        """
        props = """
<t:FieldURI FieldURI="item:Attachments"/>
<t:FieldURI FieldURI="item:HasAttachments"/>"""

        item_id, item_chkey = itemid
        item = self.get_item((item_id, item_chkey),shape="IdOnly",
                            extra_props=props)
      

        # Find all attachments
        et = ET.XML(item)
        attachments = elementsearch(et, t('ItemAttachment'), True)

        def name_filter(e):
            t_name = e.find(t('Name'))
            if t_name == None: return False
            return t_name.text == name

        attachments = filter(name_filter, attachments)

        # if len(attachments) > 1: oops?
        if len(attachments) == 0:
            return None

        # Just take the first for now
        attachment = attachments[0]
        attachment_id = attachment.find(t('AttachmentId')).attrib['Id']

        return self.get_attachment(attachment_id)


    def get_attached_note(self, itemid, name):
        """
        Get an attached note created by `createAttachedNote'
        """

        attachment = self.get_named_attachment(itemid, name)
        at_elem = ET.XML(attachment) # feilsjekking
        
        body = elementsearch(at_elem, t('Body'))
        return body.text

    def delete_attachment(self, attId):
        if not type(attId) == list:
            attId = [attId]

        attachments = ""
        for aid in attId:
            attachments += "<t:AttachmentId Id=\"%s\"/>" % aid

        return self.msquery("""
<DeleteAttachment>
  <AttachmentIds>%s</AttachmentIds>
</DeleteAttachment>
""" % attachments)


    def create_attached_note(self, itemid, name, content):
        """
        Create an Attachment to itemid = (parent_id,parent_chkey)
        """
        parent_id, parent_chkey = itemid

        return self.msquery("""
<CreateAttachment>
  <ParentItemId Id="%s" ChangeKey="%s" />
  <Attachments>
    <t:ItemAttachment>
      <t:Name>%s</t:Name>
      <t:Message>
        <t:Body BodyType="Text">%s</t:Body>
      </t:Message>
    </t:ItemAttachment>
  </Attachments>
</CreateAttachment>
""" % (parent_id, parent_chkey, name, content))


    def delete_named_attachment(self, itemid, name):
        attachment = self.get_named_attachment(itemid, name)
        at_elem = ET.XML(attachment)
        print attachment

        # TODO: feilsjekking
        a_id_elem = elementsearch(at_elem, t('AttachmentId'))
        a_id = a_id_elem.attrib['Id']

        return self.delete_attachment(a_id)

    def replace_attachment(self, itemid, name, new_content):
        self.delete_named_attachment(itemid, name)
        return self.create_attached_note(itemid, name, new_content)


    def find_items_with_subject(self, subject):
        items = self.get_all_calendar_items()
        cal = Calendar.from_xml(items)

        for i in cal.calendar_items:
            if i.get('t:Subject') != subject:
                cal.remove_calendaritem(i)

        return ET.tostring(cal.et)
