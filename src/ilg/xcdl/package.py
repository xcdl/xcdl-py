# -*- coding: utf-8 -*-

from ilg.xcdl.component import Component

class Package(Component):
    
    
    def __init__(self, **kwargs):
        
        self.unavailableKeywords = ['computed', 'isConfigurable', 
                    'valueType', 'valueFormat', 'legalValues']

        super(Package,self).__init__(**kwargs)

        # ---------------------------------------------------------------------
        self._isLoaded = False
        
        key = 'loadPackages'
        self._loadPackagesList = None
        if key in self._kwargs:
            self._loadPackagesList = self._kwargs[key]
            del self._kwargs[key]

        key = 'buildIncludeFolders'
        self._buildIncludeFoldersList = None
        if key in self._kwargs:
            self._buildIncludeFoldersList = self._kwargs[key]
            del self._kwargs[key]
        
        return
    
    
    # -------------------------------------------------------------------------
    def getLoadPackagesList(self):
        
        return self._loadPackagesList


    def isLoaded(self):
        
        return self._isLoaded
    
    
    # return the number of nodes loaded, may be higher than 1 if
    # parents were not yet loaded
    def setIsLoadedRecursive(self):
        
        updated = 0
        if self._isLoaded:
            return updated
        
        self._isLoaded=True        
        updated = 1
        
        if self._treeParent == None:
            return updated
        
        # if the parent exists, enable it too
        updated += self._treeParent.setIsLoadedRecursive()
        return updated
        
    
    def getBuildIncludeFolders(self):
        
        return self._buildIncludeFoldersList
    
    
    # always return a list, not None
    def getBuildIncludeFoldersRecursive(self):
        
        localList = []
        if self._buildIncludeFoldersList != None:
            localList.extend(self._buildIncludeFoldersList)
        
            
        if self._treeParent != None:
            parentPackageTreeNode = self._treeParent.getPackageTreeNode()
            if parentPackageTreeNode != None:
                localList.extend(parentPackageTreeNode.getBuildIncludeFoldersRecursive())
 
        return localList
    
