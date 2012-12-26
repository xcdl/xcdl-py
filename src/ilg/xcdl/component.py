# -*- coding: utf-8 -*-

from ilg.xcdl.object import Object

class Component(Object):
    
    
    def __init__(self, **kwargs):
        
        super(Component,self).__init__(**kwargs)
        
        if 'scripts' in self._kwargs:
            self._scriptsList = self._kwargs['scripts']
            del self._kwargs['scripts']

        if 'basePath' in self._kwargs:
            self._basePath = self._kwargs['basePath']
            del self._kwargs['basePath']

        return
    

    def getObjectType(self):
        
        return 'component'


    def getScripts(self):
        
        return self._scriptsList


    
