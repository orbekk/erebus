from Queue import Queue

def elementsearch(et, name, all=False):
    """Breadth-first search in an element tree"""
    q = Queue()
    results = []
    q.put(et)

    while not q.empty():
        e = q.get()
        if e.tag == name:
            if not all:
                return e
            else:
                results.append(e)
            
        [q.put(child) for child in e]
            
    if all:
        return results
    else:
        return None
