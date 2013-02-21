# -*- coding: utf-8 -*-

from ilg.xcdl.package import Package

class Repository(Package):
    
    
    def __init__(self, **kwargs):
        
        self.unavailableKeywords = ['parent', 'computed', 'isConfigurable', 
                    'valueType', 'valueFormat', 'legalValues']
        
        super(Repository, self).__init__(**kwargs)

        # ---------------------------------------------------------------------
        self._isLoaded = False
                
        key = 'buildSubFolder'
        self._buildSubFolder = None
        if key in self._kwargs:
            self._buildSubFolder = self._kwargs[key]
            del self._kwargs[key]

        key = 'sourcesPaths'
        self._sourcesPathsList = None
        if key in self._kwargs:
            self._sourcesPathsList = self._kwargs[key]
            del self._kwargs[key]
        
        # only for repository nodes
        self._repositoryFolder = None 
           
        return
    
    
    def setRepositoryFolderAbsolutePath(self, repositoryFolder):
        
        self._repositoryFolder = repositoryFolder
        return
    
    
    def getRepositoryFolderAbsolutePath(self):
        
        return self._repositoryFolder
    

    def getBuildSubFolder(self):
        
        return self._buildSubFolder
    
    
    def getBuildSubFolderWithDefault(self):
        
        if self._buildSubFolder != None:
            return self._buildSubFolder
        
        return self.getId()
       
       
