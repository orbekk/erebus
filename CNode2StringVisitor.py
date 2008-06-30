from CNodeVisitor import *
from CNode import *

class CNode2StringVisitor(CNodeVisitor):

    def __init__(self):
        self.str = ""
        self.indent = 0

    def visit_any(self, o, indent=0):
        self.str += '    ' * indent + '{'+o.name+'}' + '\n'
        for k,v in o.attrs.iteritems():
            self.str += '    ' * indent + " - %s: %s\n" %(k,v)
        
        [self.visit(c,indent=indent+1) for c in o.children]

        return self.str

