# -*- coding: utf-8 -*-

from ilg.xcdl.component import Component

class Package(Component):
    
    
    def __init__(self, name, display, description, **kwargs):
        
        super(Package,self).__init__(name, display, description, **kwargs)
        
        return
    

    def getKind(self):
        
        return "package"

