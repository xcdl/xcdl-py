# -*- coding: utf-8 -*-

from ilg.xcdl.component import Component

class Package(Component):
    
    
    def __init__(self, **kwargs):
        
        super(Package,self).__init__(**kwargs)
        
        return
    

    def getObjectType(self):
        
        return "package"

