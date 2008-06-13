from xml.etree import *
from soapquery import *
from exchangetypes import *
from localpw import *
from namespaces import *

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
#r = q.findItems('calendar')
# cal = Calendar.fromXML(r)
# print cal.toICal().as_string()
#print r


### MAKE ITEM
# attrs = [('t:Subject', 'MIRK 3'),
#          ('t:Start'  , '2008-06-14T10:00:00+02:00'),
#          ('t:End'    , '2008-06-14T16:00:00+02:00')
#          ]
# print q.createItem(attrs)
# parent_id = "AAAUADk5NTU1NUBhbnNhdHQuaGlnLm5vAEYAAAAAAFweQ/PYr15OrbYzBHnAiuAHACOPZb+9/tdIoI9+J7qYDTsAC6b9m+QAACOPZb+9/tdIoI9+J7qYDTsADbsWUlkAAA=="
# parent_chkey = "DwAAABYAAAAjj2W/vf7XSKCPfie6mA07AA27FqHR"

# r = q.createAttachedNote(parent_id, parent_chkey, "Test", "Innhold :)")

parent_id = "AAAUADk5NTU1NUBhbnNhdHQuaGlnLm5vAEYAAAAAAFweQ/PYr15OrbYzBHnAiuAHACOPZb+9/tdIoI9+J7qYDTsAC6b9m+QAACOPZb+9/tdIoI9+J7qYDTsADbsWUlkAAA=="
parent_chkey = "DwAAABYAAAAjj2W/vf7XSKCPfie6mA07AA27FqHR"
# r = q.getItem((parent_id, parent_chkey),
#               additionalProperties='<t:FieldURI FieldURI="item:Attachments"/><t:FieldURI FieldURI="item:HasAttachments"/>')
r = q.getAttachedNote(parent_id, parent_chkey, "Test")
print r

