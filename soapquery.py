# -*- coding: utf8 -*-
from xml.etree import ElementTree as ET
from helper.etsearch import elementsearch
from namespaces import *
import httplib
import base64
import re
from re import *

# workaround for a python bug (ref. soaplib)
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

types    = "http://schemas.microsoft.com/exchange/services/2006/types"
messages = "http://schemas.microsoft.com/exchange/services/2006/messages"

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

    def do_query(self,path,query,action,extraHeaders=[]):
        headers = self.headers

        headers["SOAPAction"] = action
        headers["Content-Length"] = len(query)


        for k,v in extraHeaders:
            headers[k] = v

        conn = self.make_connection()
        conn.request("POST", path, body=query, headers=headers)

        res  = conn.getresponse()
        data = res.read()

        if str(res.status) not in ['200', '202']:
            f = open('/tmp/error.xml', 'w')
            f.write(data)
            raise Exception('Error: %s\n %s\n /tmp/error.xml' %(res.status, res.reason))

        return data

def soapmethod(f):
    def new(self, *args, **kws):
        xml = ET.XML(f(self, *args, **kws))
        body = elementsearch(xml, "{http://schemas.xmlsoap.org/soap/envelope}Body")

        if body == None:
            raise Exception("Could not find <soap:Body/> element")

        soapAction = body.getchildren()[0].tag

        return self.soapconn.do_query("/ews/Exchange.asmx",f(*args,**kws),soapAction)


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
        
        xml = ET.XML(query)
        body = elementsearch(xml, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
        if body == None: raise Exception("Could not find soap:Body element")

        soapAction = body.getchildren()[0].tag
        soapAction = re.sub('{', '', soapAction)
        soapAction = re.sub('}', '/', soapAction)
        
        return self.soapconn.do_query("/ews/Exchange.asmx",query,soapAction)
        

    def __init__(self,soapconn):
        self.soapconn = soapconn

    
    def getFolder(self,folderName):
        return self.msquery("""
<GetFolder>
  <FolderShape>
    <t:BaseShape>AllProperties</t:BaseShape>
  </FolderShape>
  <FolderIds>
    <t:DistinguishedFolderId Id=\"%s\"/>
  </FolderIds>
</GetFolder>
""" % folderName)


    def findItems(self,parentFolder,baseShape="AllProperties",extraProps=[]):
        props = ""
        for p in extraProps:
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
""" % (baseShape, props, parentFolder))


    def deleteItems(self,itemIds,deleteType="MoveToDeletedItems",
                   sendMeetingCancellations="SendToNone"):
        """
        deleteType: {HardDelete, SoftDelete, *MoveToDeletedItems*}
        sendMeetingCancellations: {*SendToNone*, SendOnlyToAll, SendToAllAndSaveCopy}
        """

        ids = ""
        if type(itemIds) == list:
            for itemid,chkey in itemIds:
                ids += """<t:ItemId Id="%s" ChangeKey="%s"/>""" %(itemid,chkey)
        else:
            ids = """<t:ItemId Id="%s" ChangeKey="%s"/>""" % itemIds
        
        return self.msquery("""
<DeleteItem DeleteType="%s"
            SendMeetingCancellations="%s">
  <ItemIds>
    %s
  </ItemIds>
</DeleteItem>
""" %(deleteType, sendMeetingCancellations, ids))

    def createItem(self,calendarItems,sendMeetingInvitations="SendToNone"):
        """
        sendMeetingCancellations: {*SendToNone*, SendOnlyToAll, SendToAllAndSaveCopy}
        """

        return self.msquery("""
<CreateItem SendMeetingInvitations="%s">
  <Items>
    %s
  </Items>      
</CreateItem>
"""%(sendMeetingInvitations,
     calendarItems))


    def getItem(self, itemIds, shape="AllProperties",
                extraProps=""):
        """
        Get an item
        """
        props = ""
        for p in extraProps:
            props += "<t:FieldURI FieldURI=\"%s\"/>" % p

        if props != "":
            props = """
<t:AdditionalProperties>
  %s
</t:AdditionalProperties>""" % props

        ids = ""
        if type(itemIds) == list:
            for itemid,chkey in itemIds:
                ids += """<t:ItemId Id="%s" ChangeKey="%s"/>""" %(itemid,chkey)
        else:
            ids = """<t:ItemId Id="%s" ChangeKey="%s"/>""" % itemIds
        
        
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


    def getAllItemsForCalendar(self):
        """
        Return all items with all needed properties
        """
        r = ET.XML(self.findItems('calendar', baseShape="IdOnly"))
        id_elems = elementsearch(r, t('ItemId'), all=True)
        item_ids = [(i.attrib['Id'], i.attrib['ChangeKey']) for i in id_elems]

        return self.getItem(item_ids, extraProps=['item:Body'])


    def getAttachment(self, ids):
        if not type(ids) == list:
            ids = [ids]

        itemIds = ""
        for i in ids:
            itemIds += '<t:AttachmentId Id="%s"/>' % i

        return self.msquery("""
<GetAttachment>
  <AttachmentIds>
  %s
  </AttachmentIds>
</GetAttachment>
""" % itemIds)


    def getNamedAttachment(self, itemId, name):
        """
        Return the attachment with name `name'
        """
        props = """
<t:FieldURI FieldURI="item:Attachments"/>
<t:FieldURI FieldURI="item:HasAttachments"/>"""

        item_id, item_chkey = itemId
        item = self.getItem((item_id, item_chkey),shape="IdOnly",
                            extraProps=props)
      

        # Find all attachments
        et = ET.XML(item)
        attachments = elementsearch(et, t('ItemAttachment'), True)

        def nameFilter(e):
            t_name = e.find(t('Name'))
            if t_name == None: return False
            return t_name.text == name

        attachments = filter(nameFilter, attachments)

        # if len(attachments) > 1: oops?
        if len(attachments) == 0:
            return None

        # Just take the first for now
        attachment = attachments[0]
        attachment_id = attachment.find(t('AttachmentId')).attrib['Id']

        return self.getAttachment(attachment_id)


    def getAttachedNote(self, itemId, name):
        """
        Get an attached note created by `createAttachedNote'
        """

        attachment = self.getNamedAttachment(itemId, name)
        at_elem = ET.XML(attachment) # feilsjekking
        
        body = elementsearch(at_elem, t('Body'))
        return body.text

    def deleteAttachment(self, attId):
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


    def createAttachedNote(self, itemId, name, content):
        """
        Create an Attachment to itemId = (parent_id,parent_chkey)
        """
        parent_id, parent_chkey = itemId

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


    def deleteNamedAttachment(self, itemId, name):
        attachment = self.getNamedAttachment(itemId, name)
        at_elem = ET.XML(attachment)
        print attachment

        # TODO: feilsjekking
        a_id_elem = elementsearch(at_elem, t('AttachmentId'))
        a_id = a_id_elem.attrib['Id']

        return self.deleteAttachment(a_id)

    def replaceAttachment(self, itemId, name, new_content):
        self.deleteNamedAttachment(itemId, name)
        return self.createAttachedNote(itemId, name, new_content)
