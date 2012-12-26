# -*- coding: utf-8 -*-

from ilg.xcdl.object import Object
from ilg.xcdl.flavor import FlavorBool

class Option(Object):
    
    
    def __init__(self, **kwargs):
        
        super(Option,self).__init__(**kwargs)
        
        # ---------------------------------------------------------------------
        self._flavor = FlavorBool()

        return
    

