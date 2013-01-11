# -*- coding: utf-8 -*-

from ilg.xcdl.object import Object

class Configuration(Object):
    
    
    def __init__(self, **kwargs):
        
        super(Configuration,self).__init__(**kwargs)
        
        self._childrenList = None
        key = 'children'
        if key in self._kwargs:
            self._childrenList = self._kwargs[key]
            del self._kwargs[key]

        self._scriptsList = None
        key = 'scripts'
        if key in self._kwargs:
            self._scriptsList = self._kwargs[key]
            del self._kwargs[key]

        key = 'options'
        self._optionsList = None
        if key in self._kwargs:
            self._optionsList = self._kwargs[key]
            del self._kwargs[key]
        
        key = 'buildFolder'
        self._buildFolder = None
        if key in self._kwargs:
            self._buildFolder = self._kwargs[key]
            del self._kwargs[key]

        key = 'preprocessorSymbols'
        self._preprocessorSymbolsList = None
        if key in self._kwargs:
            self._preprocessorSymbolsList = self._kwargs[key]
            del self._kwargs[key]
            
        key = 'loadPackages'
        self._loadPackagesList = None
        if key in self._kwargs:
            self._loadPackagesList = self._kwargs[key]
            del self._kwargs[key]

        key = 'artifactFileName'
        self._artifactFileName = None
        if key in self._kwargs:
            self._artifactFileName = self._kwargs[key]
            del self._kwargs[key]
            
        return


    def isLoaded(self):
        
        return False
    
    
    def getScriptsList(self):
        
        return self._scriptsList


    def getOptionsList(self):
        
        return self._optionsList
    
    
    def getBuildFolder(self):
        
        return self._buildFolder
    
    
    def getPreprocessorSymbolsList(self):
        
        return self._preprocessorSymbolsList
    
    
    def getLoadPackagesList(self):
        
        return self._loadPackagesList

    
    def getChildrenList(self):
        
        return self._childrenList


    def getArtifactFileName(self):
        
        return self._artifactFileName


    def getArtifactFileNameRecursive(self):
        
        if self._artifactFileName != None:
            return self._artifactFileName
        
        if self._treeParent != None:
            return self._treeParent.getArtifactFileNameRecursive()
        
        return None
    

    def getBuildFolderRecursiveWithSubstitutions(self):
        
        if self._buildFolder == None:            
            if self._treeParent == None:
                # end of line, return an empty string, not None
                return ''
            # return parent value
            return self._treeParent.getBuildFolderRecursiveWithSubstitutions()
        
        # check if the macro is present
        if self._buildFolder.find('$(PARENT)') == -1:
            # if not, return it as is
            return self._buildFolder

        # must perform substitution
        newStr = ''
        if self._treeParent != None:
            # get parent value
            newStr = self._treeParent.getBuildFolderRecursiveWithSubstitutions()
            
        # string substitution
        return self._buildFolder.replace('$(PARENT)', newStr)

        
        
        