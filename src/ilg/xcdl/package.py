# -*- coding: utf-8 -*-

from ilg.xcdl.component import Component

class Package(Component):
    
    
    def __init__(self, **kwargs):
        
        super(Package,self).__init__(**kwargs)
        
        key = 'loadPackages'
        self._loadPackagesList = None
        if key in self._kwargs:
            self._loadPackagesList = self._kwargs[key]
            del self._kwargs[key]
            
        return
    

    def getObjectType(self):
        
        return 'package'


    def getLoadPackagesList(self):
        
        return self._loadPackagesList
