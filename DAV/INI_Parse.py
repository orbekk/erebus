#!/usr/bin/python

from ConfigParser import SafeConfigParser

class Configuration:
    def __init__ (self, fileName):
        cp = SafeConfigParser()
        cp.read(fileName)
        self.__parser = cp
        self.fileName = fileName
        
    def __getattr__ (self, name):
        if name in self.__parser.sections():
            return Section(name, self.__parser)
        else:
            return None
            
    def __str__ (self):
        p = self.__parser
        result = []
        result.append('<Configuration from %s>' % self.fileName)
        for s in p.sections():
            result.append('[%s]' % s)
            for o in p.options(s):
                result.append('%s=%s' % (o, p.get(s, o)))
        return '\n'.join(result)

class Section:
    def __init__ (self, name, parser):
        self.name = name
        self.__parser = parser
    def __getattr__ (self, name):
        return self.__parser.get(self.name, name)

# Test
if __name__ == '__main__':
    c = Configuration('Importador.ini')
    print c.Origem.host, c.Origem.port
    