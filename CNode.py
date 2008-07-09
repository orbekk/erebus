# -*- coding: utf-8 -*-
from Queue import Queue

class CNode(object):
    """Holds a node in our Calendar"""

    def __init__(self,name="",content=None,attr=None):
        self.name = name
        self.content = content

        if attr:
            self.attr = attr
        else:
            self.attr = {}
            
        self.children = []


    def add_child(self,child):
        if not self.children.__contains__(child):
            self.children.append(child)

        child.parent = self


    def __str__(self):
        return "{%s [%s]: %s %s}" %(self.name,
                                    str(self.attr),
                                    str(self.content),
                                    [str(c) for c in self.children])


    def delete_child(self,name):
        """Delete the first child with name `name'

        returns True if a child was deleted
        """
        for i,c in zip(range(len(self.children)), self.children):
            if c.name == name:
                self.children.pop(i)
                return True

        return False


    def search(self,name,all=False,depth=None,keep_depth=False):
        """Breadth-first search for one or more elements

        all: if True, find all matching items
        depth: how far to search for items (None means infinite depth)
        keep_depth: whenever we reach an element, don't search *deeper* in
            the tree for additional elements (only relevant when all=True)
        """
        q = Queue()
        results = []
        q.put(self)

        if depth == None: depth = -2
        this_level = 1
        next_level = 0

        while depth != -1 and not q.empty():
            if this_level == 0:
                depth -= 1
                this_level = next_level
                next_level = 0

            # TODO: check if this is off by one
            e = q.get()
            this_level -= 1

            if e.name == name:
                if keep_depth:
                    # This is the last level
                    depth = 0 
                if not all:
                    return e
                else:
                    results.append(e)

            for child in e.children:
                q.put(child)
                next_level += 1

        if all:
            return results
        else:
            return None

