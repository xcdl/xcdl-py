# -*- coding: utf-8 -*-

from ilg.xcdl.object import Object

class Interface(Object):
    
    
    def __init__(self, **kwargs):
        
        super(Interface,self).__init__(**kwargs)
        
        return

    
    def getDefaultIsEnabled(self):
        
        # interfaces start as enabled
        return True


