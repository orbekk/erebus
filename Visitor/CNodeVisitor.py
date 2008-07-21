# -*- coding: utf-8 -*-
from CNode import *

class MissingVisitor(Exception):
    def __init__(self, visitor):
        self.msg = visitor

    def __str__(self):
        return "Visitor %s missing\n" % self.msg

class CNodeVisitor(object):
    """The parent class of all Visitors

    Defines convenient functions to run a visitor on a tree of CNodes
    """
    
    def visit(self,obj,*args,**kws):
        """Visit a CNode

        visitor.visit(node,[args,kws]) will call the appropriate
        method in visitor for node.

        Example:
        node.name = 'VEVENT'
        visitor.visit(node,1,keyword=val) will call

            visitor.visit_VEVENT(node,1,keyword=val)

        If visitor_<name> don't exist, visit_any will be called
        instead. If visit_any don't exist, a MissingVisitor exception
        will be raised.
        """
        
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
        """Call this to visit children with name 'attr'

        Uses CNode.search to find all children and calls visit for all
        of them.
        """
        objs = obj.search(name, all=True)
        return [self.visit(o,*args,**kws) for o in objs]

    def accept1(self,obj,name,*args,**kws):
        """Call this to visit the first child with name 'attr'

        Finds the first child by obj.search (in case of a CNode this
        is a BFS)
        """
        child = obj.search(name)
        if child:
            return self.visit(child,*args,**kws)
        else:
            return None
