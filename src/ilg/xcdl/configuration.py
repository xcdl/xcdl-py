# -*- coding: utf-8 -*-

from ilg.xcdl.object import Object

class Configuration(Object):
    
    
    def __init__(self, name, display, description, **kwargs):
        
        super(Configuration,self).__init__(name, display, description, **kwargs)
        
        if 'scripts' in self._kwargs:
            self._scriptsList = self._kwargs['scripts']
            del self._kwargs['scripts']

        self._optionsList = None
        
        if 'options' in self._kwargs:
            self._optionsList = self._kwargs['options']
            del self._kwargs['options']
        
        self._buildFolder = None

        if 'buildFolder' in self._kwargs:
            self._buildFolder = self._kwargs['buildFolder']
            del self._kwargs['buildFolder']

        return
    

    def getKind(self):
        
        return "configuration"


    def getScripts(self):
        
        return self._scriptsList


    def getOptions(self):
        
        return self._optionsList
    
    
    def getBuildFolder(self):
        
        return self._buildFolder
    
    