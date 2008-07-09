# -*- coding: utf-8 -*-
from Queue import Queue

def elementsearch(et, name, all=False, depth=0):
    """Breadth-first search in an element tree

    If all is True, then find all items
    depth: how far to search for items (0 means infinite depth)
    """
    q = Queue()
    results = []
    q.put(et)

    if depth == 0: depth = -2
    this_level = 1
    next_level = 0

    while depth != -1 and not q.empty():
        if this_level == 0:
            depth -= 1
            this_level = next_level
            next_level = 0
            
        e = q.get()
        this_level -= 1

        if e.tag == name:
            if not all:
                return e
            else:
                results.append(e)

        for child in e:
            q.put(child)
            child.parent = e # Nice to have :-)
            next_level += 1

    if all:
        return results
    else:
        return None
