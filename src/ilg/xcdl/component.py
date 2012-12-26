# -*- coding: utf-8 -*-

from ilg.xcdl.object import Object
from ilg.xcdl.flavor import FlavorBool

class Component(Object):
    
    
    def __init__(self, **kwargs):
        
        super(Component,self).__init__(**kwargs)
        
        # ---------------------------------------------------------------------
        self._flavor = FlavorBool()

        # ---------------------------------------------------------------------
        self._childrenList = None
        key = 'children'
        if key in self._kwargs:
            self._childrenList = self._kwargs[key]
            del self._kwargs[key]


        # ???
        # ---------------------------------------------------------------------
        
        self._scriptsList = None
        if 'scripts' in self._kwargs:
            self._scriptsList = self._kwargs['scripts']
            del self._kwargs['scripts']

        self._basePath = None
        if 'basePath' in self._kwargs:
            self._basePath = self._kwargs['basePath']
            del self._kwargs['basePath']

        return
    

    def getChildrenList(self):
        
        return self._childrenList
    

    # ???
    # -------------------------------------------------------------------------    
    def getScriptsList(self):
        
        return self._scriptsList


    
