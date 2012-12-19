# -*- coding: utf-8 -*-

from ilg.xcdl.object import Object

class Component(Object):
    
    
    def __init__(self, name, display, description, **kwargs):
        
        super(Component,self).__init__(name, display, description, **kwargs)
        
        if 'scripts' in self._kwargs:
            self._scriptsList = self._kwargs['scripts']
            del self._kwargs['scripts']

        if 'basePath' in self._kwargs:
            self._basePath = self._kwargs['basePath']
            del self._kwargs['basePath']

        if 'platform' in self._kwargs:
            self._platform = self._kwargs['platform']
            del self._kwargs['platform']

        return
    

    def getKind(self):
        
        return "component"


    def getScripts(self):
        
        return self._scriptsList


    
