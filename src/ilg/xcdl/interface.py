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
        
        return

    
    def getDefaultIsEnabled(self):
        
        # interfaces start as enabled
        return True


    def getDefaultIsConfigurable(self):
        
        # interfaces as non configurable
        return False
    

