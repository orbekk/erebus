# -*- coding: utf-8 -*-

from Visitor.CNodeVisitor import *
from Visitor.Erebus2EWSVisitor import *
from CNode import *
from namespaces import *

class Erebus2EWSUpdate(CNodeVisitor):
    """Make an Update item, to update an item in the Exchange
    calendar.

    This is an internal class used by ExchangeBackend
    """

    trans = {
        'Subject': 'item:Subject',
        'Start': 'calendar:Start',
        'End': 'calendar:End',
        'IsAllDayEvent': 'calendar:IsAllDayEvent',
        'Location': 'calendar:Location',
        'MeetingTimeZone': 'calendar:MeetingTimeZone',
        'Sensitivity': 'item:Sensitivity',
        'DateTimeCreated': 'item:DateTimeCreated',
        'Body': 'item:Body'}

    def __init__(self,cnode):
        self.ebus = cnode

    def run(self):
        self.ews = Erebus2SimpleEWSVisitor(self.ebus).run()
        self.updates = CNode('Updates')
        self.visit(self.ews)
        AddNamespaceVisitor(self.updates,types).run()
        return self.updates

    def _create_field_uri(self,uri):
        """Add a field URI to updates.

        Warning: An item corresponding to `uri' must be added to
          self.updates after a call to this method
        """
        u = CNode('FieldURI')
        u.attr['FieldURI'] = uri
        return u

    def _make_parent(self,path):
        """Make a "tree" of CNodes as a parent for an update value,

        Example:

        self._make_parent(['CalendarItem','Subject'])

        => a CNode('Subject') node with a CNode('CalendarItem') parent

        returns:
        (topmost parent, the last child), in the example:
           (the Subject CNode, the CalendarItem CNode)
        """
        child = CNode(path.pop())

        c = child
        while len(path):
            p = CNode(path.pop())
            p.add_child(c)
            c = p
        parent = c

        return (parent, child)

    def visit_any(self,e):
        """Check the trans table"""
        if self.trans.has_key(e.name):
            (p,c) = self._make_parent(['CalendarItem'])
            c.add_child(e)

            uri = self._create_field_uri(self.trans[e.name])

            setitem = CNode('SetItemField')
            setitem.add_child(uri)
            setitem.add_child(p)
            
            self.updates.add_child(setitem)

        # Visit children
        for c in e.children:
            self.visit(c)
        
