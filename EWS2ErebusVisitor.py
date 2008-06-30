from CNodeVisitor import *
from CNode import *
from namespaces import *

class StripNamespaceVisitor(CNodeVisitor):
    def visit_any(self, o):
        o.name = no_namespace(o.name)
        [self.visit(c) for c in o.children]

class EWS2ErebusVisitor(CNodeVisitor):

    def __init__(self,cnode):
        self.timezones = []
        # Strip namespace from cnode
        StripNamespaceVisitor().visit(cnode)

        self.calendaritems = []
        
        for item in cnode.search('CalendarItem',all=True,keep_depth=True):
            self.calendaritems.append(item)

    def visit_start(self):
        print "i has %d calendaritems" % len(self.calendaritems)
        [self.visit(ci) for ci in self.calendaritems]

    def visitCalendarItem(self,ci):
        pass

    def strip_tag(self, o):
        o.name = no_namespace(o.name)

#     def visit_any(self, o, indent=0):
#         self.str += '    ' * indent + '{'+o.name+'}' + '\n'
#         self.str += '    ' * indent + '  '+str(o.content)+ '\n'

#         for k,v in o.attrs.iteritems():
#             self.str += '    ' * indent + " - %s: %s\n" %(k,v)

#         [self.visit(c,indent=indent+1) for c in o.children]

#         return self.str

