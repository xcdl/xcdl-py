# -*- coding: utf-8 -*-

from ilg.xcdl.errorWithDescription import ErrorWithDescription


class Object(object):
    
    # static member
    _objectsList = None

    
    @staticmethod
    def setList(oList):
        
        Object._objectsList = oList
        return


    @staticmethod    
    def getList():
        
        return Object._objectsList
    
    
    def __init__(self, **kwargs):
        
        # store the current keywords args dictionary. 
        # will be consumed on each constructor
        self._kwargs = kwargs

        if Object._objectsList != None:
            Object._objectsList.append(self)
        
        # store given values
        self._id = None
        if 'id' in self._kwargs:
            self._id = self._kwargs['id']
            del self._kwargs['id']
        else:
            raise ErrorWithDescription('Mandatory id missing')
            
        self._name = None        
        if 'name' in self._kwargs:
            self._name = self._kwargs['name']
            del self._kwargs['name']

        self._description = None
        if 'description' in self._kwargs:
            self._description = self._kwargs['description']
            del self._kwargs['description']
                
        # initialise empty members
        self._treeParent = None
        self._treeChildrenList = None
        self._scriptsList = None        
        self._basePath = None        
        self._parentName = None
        
        # consume known args
        #if 'parent' in self._kwargs:
        #    self._parentName = self._kwargs['parent']
        #    del self._kwargs['parent']
        
        self._sourcesPathsList = None
        if 'sourcesPaths' in self._kwargs:
            self._sourcesPathsList = self._kwargs['sourcesPaths']
            del self._kwargs['sourcesPaths']

        self._compileList = None
        if 'compile' in self._kwargs:
            self._compileList = self._kwargs['compile']
            del self._kwargs['compile']

        self._requiresList = None
        if 'requires' in self._kwargs:
            self._requiresList = self._kwargs['requires']
            del self._kwargs['requires']

        self._headerPath = None
        if 'headerPath' in self._kwargs:
            self._headerPath = self._kwargs['headerPath']
            del self._kwargs['headerPath']

        self._headerDefinition = None
        if 'headerDefinition' in self._kwargs:
            self._headerDefinition = self._kwargs['headerDefinition']
            del self._kwargs['headerDefinition']

        self._childrenList = None
        if 'children' in self._kwargs:
            self._childrenList = self._kwargs['children']
            del self._kwargs['children']

        self._kind = None
        if 'kind' in self._kwargs:
            self._kind = self._kwargs['kind']
            del self._kwargs['kind']

        return


    def getObjectType(self):
        
        return None
    
    
    def getId(self):
        
        return self._id
    
    
    def getName(self):
        
        return self._name
    
    
    def getDescription(self):
        
        return self._description
    

    # climb the hierarchy until found
    def getBasePath(self):
        
        # if explicitly set, return it
        if self._basePath != None:
            return self._basePath
        
        # if there is no parent, then no other chance left
        if self._treeParent == None:
            return None
        
        # return the parent base path
        return self._treeParent.getBasePath()
    
    
    def setTreeParent(self, parent):
        
        self._treeParent = parent
        
        return
    
    
    def getTreeParent(self):
        
        return self._treeParent
    
    
    def addTreeChild(self, child):
        
        if self._treeChildrenList == None:
            self._treeChildrenList = []
            
        self._treeChildrenList.append(child)
        
        return
    
    
    def getTreeChildren(self):
        
        return self._treeChildrenList


    def getParentName(self):
        
        return self._parentName
    
    
    def getNonParsedKeywords(self):
        
        return self._kwargs;
    
    
    # climb the hierarchy until found
    def getSourcePaths(self):
        
        # if explicitly set, return it
        if self._sourcesPathsList != None:
            return self._sourcesPathsList
        
        # if there is no parent, then no other chance left
        if self._treeParent == None:
            return None
        
        # return the parent base path
        return self._treeParent.getSourcePaths()


    def getCompile(self):
        
        return self._compileList
    
    
    def getRequires(self):
        
        return self._requiresList
    
        
    def getHeaderPath(self):
        
        return self._headerPath
    
    
    def getHeaderDefinition(self):
        
        return self._headerDefinition
    
    
    def getChildren(self):
        
        return self._childrenList
    
    
    def getKind(self):
        
        return self._kind
    
    
    def setKind(self, kind):
        
        self._kind = kind
        
        
    