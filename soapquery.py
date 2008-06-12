from xml.etree import ElementTree as ET
from helper.etsearch import elementsearch
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


    def findItems(self,parentFolder,baseShape="AllProperties"):
        return self.msquery("""
<FindItem Traversal="Shallow">
  <ItemShape>
    <t:BaseShape>%s</t:BaseShape>
  </ItemShape>
  <ParentFolderIds>
    <t:DistinguishedFolderId Id="%s"/>
  </ParentFolderIds>
</FindItem>
""" % (baseShape, parentFolder))


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

    def createItem(self,props,sendMeetingInvitations="SendToNone"):
        """
        sendMeetingCancellations: {*SendToNone*, SendOnlyToAll, SendToAllAndSaveCopy}
        """

        # This is suboptimal. Better use a element tree
        xml_fields = ""
        for k,v in props:
            xml_fields += ("<%s>%s</%s>" %(k,v,k))

        return self.msquery("""
<CreateItem SendMeetingInvitations="%s">
  <Items>
    <t:CalendarItem>
    %s
    </t:CalendarItem>
  </Items>      
</CreateItem>
"""%(sendMeetingInvitations,
     xml_fields))
        
        
    

# createItemQuery = msquery("""
# <CreateItem SendMeetingInvitations="SendToNone">
#   <Items>
#     <t:CalendarItem>
#       <t:Subject>Bli tuktet av StianH</t:Subject>
#       <t:Start>2008-06-12T08:00:00+01:00</t:Start>
#       <t:End>2008-06-12T16:00:00+01:00</t:End>
#     </t:CalendarItem>
#   </Items>      
# </CreateItem>
# """)

# getItem = msquery("""
# <GetItem>
#   <ItemShape>
#     <t:BaseShape>Default</t:BaseShape>
#   </ItemShape>
# </GetItem>
# """)

# findItems = msquery("""
# <FindItem Traversal="Shallow">
#   <ItemShape>
#     <t:BaseShape>AllProperties</t:BaseShape>
#   </ItemShape>
#   <ParentFolderIds>
#     <t:DistinguishedFolderId Id="calendar"/>
#   </ParentFolderIds>
# </FindItem>
# """)

