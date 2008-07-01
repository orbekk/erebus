from CNodeVisitor import *
from CNode import *

class CNode2StringVisitor(CNodeVisitor):

    def __init__(self):
        self.str = ""
        self.indent = 0

    def visit_any(self, o, indent=0):
        self.str += '    ' * indent + '{'+o.name+'}' + '\n'
        cont = o.content
        if type(cont) != str and type(cont) != unicode:
            cont = str(cont)
        
        self.str += u'    ' * indent + u'  '+cont+ u'\n'

        for k,v in o.attr.iteritems():
            self.str += '    ' * indent + " - %s: %s\n" %(k,v)

        [self.visit(c,indent=indent+1) for c in o.children]

        return self.str

