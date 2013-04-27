# -*- coding: utf-8 -*-

from ilg.xcdl.node import ActiveNode

class Component(ActiveNode):
    
    
    def __init__(self, **kwargs):
        
        super(Component,self).__init__(**kwargs)
        

        # ---------------------------------------------------------------------
        key = 'children'
        self._childrenList = None
        if key in self._kwargs:
            self._childrenList = self._kwargs[key]
            del self._kwargs[key]


        # ---------------------------------------------------------------------
        
        key = 'includeFiles'
        self._includesList = None
        if key in self._kwargs:
            self._includesList = self._kwargs[key]
            del self._kwargs[key]

        key = 'basePath'
        self._basePath = None
        if key in self._kwargs:
            self._basePath = self._kwargs[key]
            del self._kwargs[key]

        key = 'childrenHeaderFile'
        self._childrenHeaderFile = None
        if key in self._kwargs:
            self._childrenHeaderFile = self._kwargs[key]
            del self._kwargs[key]


        return
    


    def getChildrenList(self):
        
        return self._childrenList


    def getChildrenHeaderFile(self):
        
        return self._childrenHeaderFile
    

    # -------------------------------------------------------------------------    
    def getIncludesList(self):
        
        return self._includesList

