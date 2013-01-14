# -*- coding: utf-8 -*-

from ilg.xcdl.object import Object

class Component(Object):
    
    
    def __init__(self, **kwargs):
        
        super(Component,self).__init__(**kwargs)
        

        # ---------------------------------------------------------------------
        key = 'children'
        self._childrenList = None
        if key in self._kwargs:
            self._childrenList = self._kwargs[key]
            del self._kwargs[key]


        # ---------------------------------------------------------------------
        
        key = 'includes'
        self._includesList = None
        if key in self._kwargs:
            self._includesList = self._kwargs[key]
            del self._kwargs[key]

        key = 'basePath'
        self._basePath = None
        if key in self._kwargs:
            self._basePath = self._kwargs[key]
            del self._kwargs[key]

        return
    

    def getChildrenList(self):
        
        return self._childrenList
    

    # -------------------------------------------------------------------------    
    def getIncludesList(self):
        
        return self._includesList


    def getDefaultIsEnabled(self):
        
        # components start as enabled
        return True
    
