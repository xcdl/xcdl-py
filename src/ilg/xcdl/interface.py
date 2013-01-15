# -*- coding: utf-8 -*-

from ilg.xcdl.object import Object

from ilg.xcdl.errorWithDescription import ErrorWithDescription

class Interface(Object):
    
    
    def __init__(self, **kwargs):
        
        super(Interface,self).__init__(**kwargs)
        
        key='isConfigurable'
        self._isConfigurableExpression = None
        if key in self._kwargs:
            del self._kwargs[key]
            raise ErrorWithDescription('Unsupported property {0}'.format(key))

        key='computed'
        self._computedExpression = None
        if key in self._kwargs:
            del self._kwargs[key]
            raise ErrorWithDescription('Unsupported property {0}'.format(key))

        key='defaultValue'
        self._defaultValueExpression = None
        if key in self._kwargs:
            del self._kwargs[key]
            raise ErrorWithDescription('Unsupported property {0}'.format(key))

        key='valueType'
        self._valueType = 'int'
        if key in self._kwargs:
            del self._kwargs[key]
            raise ErrorWithDescription('Unsupported property {0}'.format(key))

        key='implements'
        self._implementsList = None
        if key in self._kwargs:
            del self._kwargs[key]
            raise ErrorWithDescription('Unsupported property {0}'.format(key))
        
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


