# -*- coding: utf8 -*-
from CNode import *

class MissingVisitor(Exception):
    def __init__(self, visitor):
        self.msg = str

    def __str__(self):
        return "Visitor %s missing" % self.visitor

class CNodeVisitor(object):
    def visit(self,obj,*args,**kws):
        method_name = "visit_%s" % obj.name

        if obj.name and hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(obj,*args,**kws)
        else:
            if hasattr(self, 'visit_any'):
                return self.visit_any(obj,*args,**kws)
            else:
                raise MissingVisitor("visit_%s" % method_name)

    def accept(self,obj,name,*args,**kws):
        """Call this to visit children with name 'attr'"""
        objs = obj.search(name, all=True)
        return [self.visit(o,*args,**kws) for o in objs]

    def accept1(self,obj,name,*args,**kws):
        """Call this to visit the first child with name 'attr'"""
        child = obj.search(name)
        if child:
            return self.visit(child,*args,**kws)
        else:
            return None
