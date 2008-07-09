# -*- coding: utf-8 -*-
from Visitor.CNodeVisitor import *
from CNode import *

class ToStringVisitor(CNodeVisitor):

    def __init__(self, with_types=False):
        self.str = ""
        self.with_types = with_types
        self.indent = 0

    def visit_any(self, o, indent=0):
        if self.with_types:
            displayname = o.name + ' ' + str(type(o.name))
        else:
            displayname = o.name

        self.str += '    ' * indent + '{'+displayname+'}' + '\n'
        cont = o.content

        # usj og fysj
        if type(cont) != str and type(cont) != unicode:
            cont = str(cont)
        if type(cont) == str:
            cont = unicode(cont,'utf8')

        if self.with_types:
            cont = cont + " (: %s)" % str(type(o.content))

        self.str += u'    ' * indent + u'  '+cont+ u'\n'

        for k,v in o.attr.iteritems():
            if self.with_types:
                k = "(%s : %s)" % (k, str(type(k)))
                v = v + " (: %s)" % str(type(v))
            self.str += '    ' * indent + " - %s: %s\n" %(k,v)

        [self.visit(c,indent=indent+1) for c in o.children]

        return self.str

