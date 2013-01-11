# -*- coding: utf-8 -*-

from ilg.xcdl.component import Component

class Package(Component):
    
    
    def __init__(self, **kwargs):
        
        super(Package,self).__init__(**kwargs)

        # ---------------------------------------------------------------------
        self._isLoaded = False
        
        key = 'loadPackages'
        self._loadPackagesList = None
        if key in self._kwargs:
            self._loadPackagesList = self._kwargs[key]
            del self._kwargs[key]

        key = 'buildSubFolder'
        self._buildSubFolder = None
        if key in self._kwargs:
            self._buildSubFolder = self._kwargs[key]
            del self._kwargs[key]

        key = 'buildIncludeFolders'
        self._buildIncludeFoldersList = None
        if key in self._kwargs:
            self._buildIncludeFoldersList = self._kwargs[key]
            del self._kwargs[key]
        
        # set only to root nodes
        self._repositoryFolder = None 
           
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
        

    def getDefaultIsEnabled(self):
        
        # packages start as enabled
        return True
    
    
    def getBuildSubFolder(self):
        
        return self._buildSubFolder
    
    
    def getBuildSubFolderWithDefault(self):
        
        if self._buildSubFolder != None:
            return self._buildSubFolder
        
        return self.getId()
       
       
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
    
    
    def setRepositoryFolderAbsolutePath(self, repositoryFolder):
        
        self._repositoryFolder = repositoryFolder
        return
    
    
    def getRepositoryFolderAbsolutePath(self):
        
        return self._repositoryFolder
    
