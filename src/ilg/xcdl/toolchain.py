# -*- coding: utf-8 -*-

# Copyright (C) 2013 Liviu Ionescu.
# This file is part of the XCDL distribution.

from ilg.xcdl.object import Object
from ilg.xcdl.errorWithDescription import ErrorWithDescription

class Toolchain(Object):
    
    allowedPropertiesList=[
        'compilerObjectsExtension',
        'compilerDepsOptions',
        'compilerOutputOptions',
        'compilerInputOptions',
        'compilerWarningOptions',
        'compilerMiscOptions',
        'compilerDebugOptions',
        'compilerOptimisationOptions',
        'compilerCpu',
        
        'linkerMiscOptions',
        
        'programNamePrefix',
        'programNameSuffix',

        'makeObjectsVariable',
    ]
    
    def __init__(self, **kwargs):
        
        super(Toolchain,self).__init__(**kwargs)
        
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


        self._toolsDict = {}
        for key in ['cc', 'cpp', 'ld', 'asm']:
            if key in self._kwargs:
                tool = self._kwargs[key]
                
                # store a link back to the toolchain in each tool
                tool.setToolchain(self)
                tool.setToolName(key)
                
                self._toolsDict[key] = tool
                del self._kwargs[key]

        self._properties = {}
        for key in Toolchain.allowedPropertiesList:
            if key in self._kwargs:
                self._properties[key] = self._kwargs[key]
                del self._kwargs[key]

        # ---------------------------------------------------------------------
        
        key = 'platformSystem'
        self._platformSystem = None
        if key in self._kwargs:
            self._platformSystem = self._kwargs[key]
            del self._kwargs[key]
            
        return
    

    def getChildrenList(self):
        
        return self._childrenList
    

    # -------------------------------------------------------------------------    
    def getIncludesList(self):
        
        return self._includesList


    def getToolsDict(self):
        
        return self._toolsDict
    

    def getTool(self, key):
        
        if key in self._toolsDict:
            return self._toolsDict[key]
        
        return None
    
    
    def getToolRecursive(self, key):
        
        if key in self._toolsDict:
            return self._toolsDict[key]
        
        parentNode = self.getTreeParent()
        if parentNode == None:
            return None
        
        return parentNode.getToolRecursive(key)


    def getProperty(self, key):
        
        if key in self._properties:
            return self._properties[key]
        
        return None

    
    def getPropertyRecursive(self, key):
        
        if key in self._properties:
            return self._properties[key]
        
        parentNode = self.getTreeParent()
        if parentNode == None:
            return None
        
        if parentNode.getObjectType() == 'Toolchain':
            return parentNode.getPropertyRecursive(key)
        
        return None


    def getPropertyRecursiveWithDefault(self, key):
        
        value = self.getPropertyRecursive(key)
        if value != None:
            return value
        
        # here must supply an appropriate default
        if key == 'makeObjectsVariable':
            return 'OBJS'
        elif key == 'compilerObjectsExtension':
            return 'o'
        elif key == 'linkerMiscOptions':
            return ''
        elif key == 'compilerInputOptions':
            return '"$<"'
        elif key == 'compilerOutputOptions':
            return '-o "$@"'
        elif key == 'compilerDepsOptions':
            return '-MMD -MP'
        elif key == 'compilerMiscOptions':
            return '-fmessage-length=0 -c'
        elif key == 'compilerWarningOptions':
            return '-Wall'
        elif key == 'compilerDebugOptions':
            return '-g'
        elif key == 'compilerOptimisationOptions':
            return '-O'
        
        return None
        
    # Tool related methods
    
    def getToolProgramNameRecursive(self, key):
        
        if key in self._toolsDict:
            tool = self._toolsDict[key]
            if tool != None:
                programName = tool.getProgramName()
                if programName != None:
                    return programName
                    
        parentNode = self.getTreeParent()
        if parentNode == None:
            return None
        
        return parentNode.getToolProgramNameRecursive(key)


    def getToolProgramNameRecursiveWithSubstitutions(self, key):
        
        programName = self.getToolProgramNameRecursive(key)
        
        if programName.find('$(PREFIX)') != -1:
            prefix = self.getPropertyRecursive('programNamePrefix')
            if prefix == None:
                prefix=''
                
            programName = programName.replace('$(PREFIX)', prefix)

        if programName.find('$(SUFFIX)') != -1:
            suffix = self.getPropertyRecursive('programNameSuffix')
            if suffix == None:
                suffix = ''
                
            programName = programName.replace('$(SUFFIX)', suffix)

        return programName


    def getToolDescriptionRecursive(self, key):
        
        if key in self._toolsDict:
            tool = self._toolsDict[key]
            if tool != None:
                description = tool.getDescription()
                if description != None:
                    return description
                    
        parentNode = self.getTreeParent()
        if parentNode == None:
            return None
        
        return parentNode.getToolDescriptionRecursive(key)

        
class Tool():
    
    def __init__(self, **kwargs):

        self._kwargs = kwargs
        self._toolchain = None;
        self._toolName = None
        
        key = 'programName'
        if key in self._kwargs:
            self._programName = self._kwargs[key]
            del self._kwargs[key]
        else:
            raise ErrorWithDescription('Mandatory Tool() programName missing')

        key = 'description'
        if key in self._kwargs:
            self._description = self._kwargs[key]
            del self._kwargs[key]
        else:
            raise ErrorWithDescription('Mandatory Tool() description missing')

        key = 'options'
        self._options = None
        if key in self._kwargs:
            self._options = self._kwargs[key]
            del self._kwargs[key]
            
        return


    def setToolchain(self, toolchain):
        
        self._toolchain = toolchain
        return


    def setToolName(self, name):
        
        self._toolName = name
        return


    def getToolchain(self):
        
        return self._toolchain


    def getProgramName(self):
        
        return self._programName

    
    def getDescription(self):
        
        return self._description
    
    
    def getOptions(self):
        
        return self._options
    
    
    def getPlatformSystem(self):
        
        return self._platformSystem
    
    
    