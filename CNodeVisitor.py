# -*- coding: utf8 -*-
from CNode import *

class MissingVisitor(Exception):
    def __init__(self, visitor):
        self.msg = str

    def __str__(self):
        return "Visitor %s missing" % self.visitor

class CNodeVisitor(object):
    def visit(self,obj,*args,**kws):
        method_name = "visit%s" % obj.name

        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(obj,*args,**kws)
        else:
            if hasattr(self, 'visit_any'):
                return self.visit_any(obj,*args,**kws)
            else:
                raise MissingVisitor("visit%s" % method_name)

    def accept(self,obj,attr):
        """Call this to visit children with name 'attr'"""
        return [self.visit(o) for o in getattr(obj, attr)]

    def accept1(self,obj,attr):
        """Call this to visit the first child with name 'attr'"""
        its = getattr(obj, attr)
        if len(its) > 0:
            self.visit(its[0])
        else:
            return None
