
class CNode(object):
    """Holds a node in the Calendar (xml or ical)"""
    
    def __init__(self,name="",content=None,attrs={}):
        self.name = name
        self.content = content
        self.attrs = attrs
        self.children = []

    def add_child(self,child):
        if not self.children.__contains__(child):
            self.children.append(child)

        child.parent = self

    def __str__(self):
        return "{%s [%s]: %s %s}" %(self.name,
                                    str(self.attrs),
                                    str(self.content),
                                    [str(c) for c in self.children])
    
