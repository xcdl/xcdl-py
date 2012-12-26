# -*- coding: utf-8 -*-

from ilg.xcdl.component import Component
from ilg.xcdl.flavor import FlavorBoolData

class Package(Component):
    
    
    def __init__(self, **kwargs):
        
        super(Package,self).__init__(**kwargs)

        # ---------------------------------------------------------------------
        self._flavor = FlavorBoolData()

        # ---------------------------------------------------------------------
        self._isLoaded = False
        
        key = 'loadPackages'
        self._loadPackagesList = None
        if key in self._kwargs:
            self._loadPackagesList = self._kwargs[key]
            del self._kwargs[key]
            
        return
    

    # -------------------------------------------------------------------------
    def setFlavor(self, flavorString):
        
        # do not allow packages to change flavorString
        return

    # -------------------------------------------------------------------------
    def getLoadPackagesList(self):
        
        return self._loadPackagesList

    def isLoaded(self):
        
        return self._isLoaded
    
    
    def setIsLoaded(self):
        
        updated = 0
        if self._isLoaded:
            return updated
        
        self._isLoaded=True        
        updated = 1
        
        if self._treeParent == None:
            return updated
        
        # if the parent exists, enable it too
        updated += self._treeParent.setIsLoaded()
        return updated
        
    
