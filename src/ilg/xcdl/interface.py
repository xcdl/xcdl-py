# -*- coding: utf-8 -*-

from ilg.xcdl.node import ActiveNode

from ilg.xcdl.errorWithDescription import ErrorWithDescription

class Interface(ActiveNode):
    
    
    def __init__(self, **kwargs):
        
        self.unavailableKeywords = ['computed', 'defaultValue', 'isConfigurable',
                    'valueType', 'implements']

        super(Interface, self).__init__(**kwargs)
                
        # the list where all implementations will be collected
        self._implementationsList = []
        
        return

    
    def getDefaultIsConfigurable(self):
        
        # interfaces as non configurable
        return False


    def addImplementationWithCount(self, sid):
        
        # avoid inserting multiple instances of the same implementor
        if sid not in self._implementationsList:
            self._implementationsList.append(sid)
            return 1
            
        return 0

    
    # overwrite to return the number of implementors  
    def getValue(self):
        
        if not self.isActive():
            return 0

        return len(self._implementationsList)


