from xml.etree import *
from soapquery import *
from exchangetypes import *
from localpw import *

c = SoapConn(host,False,username,password)
q = SoapQuery(c)

### DELETE ALL ITEMS:
# items = q.findItems('calendar')
# cal = Calendar.fromXML(items)
# ids = []
# for item in cal.calendarItems:
#     ids.append((item.attrs["ItemId"], item.attrs["ChangeKey"]))
# q.deleteItems(ids)    

### FIND ITEMS
r = q.findItems('calendar')
cal = Calendar.fromXML(r)
print cal.toICal().as_string()

### MAKE ITEM
# attrs = [('t:Subject', 'MIRK 3'),
#          ('t:Start'  , '2008-06-14T10:00:00+02:00'),
#          ('t:End'    , '2008-06-14T16:00:00+02:00')
#          ]
# print q.createItem(attrs)

#print c.do_query("/ews/Exchange.asmx",findItems,"FindItem")
