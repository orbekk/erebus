from Backend import Backend
from Visitor.EWS2ErebusVisitor import *
from Visitor.Erebus2EWSVisitor import *

from xml.etree import ElementTree as ET
from erebusconv import xml2cnode, cnode2xml

from soapquery import *

class ExchangeBackend(Backend):
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

    def get_all_items(self):
        items = self.query.get_all_calendar_items()
        ctree = self.__conv(items)
        
        return EWS2ErebusVisitor(ctree).run()
