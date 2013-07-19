# -*- coding: utf-8 -*-

from ilg.xcdl.node import Node

class Configuration(Node):
    
    
    def __init__(self, **kwargs):
        
        super(Configuration,self).__init__(**kwargs)
        
        self._childrenList = None
        key = 'children'
        if key in self._kwargs:
            self._childrenList = self._kwargs[key]
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

        key = 'artefactName'
        self._artefactName = None
        if key in self._kwargs:
            self._artefactName = self._kwargs[key]
            del self._kwargs[key]

        key = 'artefactExtension'
        self._artefactExtension = None
        if key in self._kwargs:
            self._artefactExtension = self._kwargs[key]
            del self._kwargs[key]

        key = 'artefactDescription'
        self._artefactDescription = None
        if key in self._kwargs:
            self._artefactDescription = self._kwargs[key]
            del self._kwargs[key]

        key = 'toolchain'
        self._toolchainId = None
        if key in self._kwargs:
            self._toolchainId = self._kwargs[key]
            del self._kwargs[key]

        key = 'buildConfigurationName'
        self._buildConfigurationName = None
        if key in self._kwargs:
            self._buildConfigurationName = self._kwargs[key]
            del self._kwargs[key]

        key = 'requirements'
        self._requiresList = None
        if key in self._kwargs:
            self._requiresList = self.enforceListOfStrings(self._kwargs[key], self._id, key)
            del self._kwargs[key]

        key = 'includeFiles'
        self._includesList = None
        if key in self._kwargs:
            self._includesList = self._kwargs[key]
            del self._kwargs[key]

        key = 'buildTargetCpuOptions'
        self._buildTargetCpuOptions = None
        if key in self._kwargs:
            self._buildTargetCpuOptions = self._kwargs[key]
            del self._kwargs[key]

        key = 'copyFiles'
        self._copyFilesList = None
        if key in self._kwargs:
            self._copyFilesList = self._kwargs[key]
            del self._kwargs[key]
            
        return


    # -------------------------------------------------------------------------    
    # just to keep dump tree happy
    def getValueType(self):
        
        return None
    

    # -------------------------------------------------------------------------    
    def getDefaultIsEnabled(self):
        
        # configurations are disabled by default
        return False
    
    # -------------------------------------------------------------------------    
    def isActive(self):
        
        return True
    
    # -------------------------------------------------------------------------    
    
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
    

    def getArtefactName(self):
        
        return self._artefactName


    def getArtefactNameRecursive(self):
        
        if self._artefactName != None:
            return self._artefactName
        
        if self._treeParent != None and self._treeParent.getObjectType() == 'Configuration':
            return self._treeParent.getArtefactNameRecursive()
        
        return None

    
    def getArtefactExtension(self):
        
        return self._artefactExtension


    def getArtefactExtensionRecursive(self):
        
        if self._artefactExtension != None:
            return self._artefactExtension
        
        if self._treeParent != None and self._treeParent.getObjectType() == 'Configuration':
            return self._treeParent.getArtefactExtensionRecursive()
        
        return None


    def getArtefactExtensionRecursiveWithDefault(self):
        
        ext = self.getArtefactExtensionRecursive()
        if ext != None:
            return ext
        
        return 'elf'
        

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
        if self._treeParent != None and self._treeParent.getObjectType() == 'Configuration':
            # get parent value
            newStr = self._treeParent.getBuildFolderRecursiveWithSubstitutions()
            
        # string substitution
        return self._buildFolder.replace('$(PARENT)', newStr)

        
    def getToolchainId(self):
        
        return self._toolchainId
    
    
    def getBuildConfigurationName(self):
        
        return self._buildConfigurationName

    
    def getRequiresList(self):
        
        return self._requiresList

    
    def getBuildTargetCpuOptions(self):
        
        return self._buildTargetCpuOptions


    def getBuildTargetCpuOptionsRecursive(self):
        
        if self._buildTargetCpuOptions != None:
            return self._buildTargetCpuOptions
        
        if self._treeParent != None and self._treeParent.getObjectType() == 'Configuration':
            return self._treeParent.getBuildTargetCpuOptionsRecursive()
        
        return None

        
    # -------------------------------------------------------------------------    
    def getIncludesList(self):
        
        return self._includesList

        