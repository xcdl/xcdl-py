# -*- coding: utf-8 -*-

from ilg.xcdl.errorWithDescription import ErrorWithDescription
from ilg.xcdl.flavor import Flavor
from ilg.xcdl.flavor import FlavorNone

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

        # initialise empty members
        self._treeParent = None
        self._treeChildrenList = None
        self._basePath = None        
        self._packageLocation = None
        
        # ---------------------------------------------------------------------
        key = 'flavor'
        if key in self._kwargs:
            self._flavor = Flavor.construct(self._kwargs[key])
            del self._kwargs[key]
        else:
            # default flavour, should be set in each object again
            self._flavor = FlavorNone()
            
        # ---------------------------------------------------------------------
        # main properties id, name, description
        # store given values
        self._id = None
        key = 'id'
        if key in self._kwargs:
            self._id = self._kwargs[key]
            del self._kwargs[key]
        else:
            raise ErrorWithDescription('Mandatory id missing')
            
        self._name = None        
        key = 'name'
        if key in self._kwargs:
            self._name = self._kwargs[key]
            del self._kwargs[key]

        self._description = None
        key = 'description'
        if key in self._kwargs:
            self._description = self._kwargs[key]
            del self._kwargs[key]
                
        self._compileList = None
        key = 'compile'
        if key in self._kwargs:
            self._compileList = self._kwargs[key]
            del self._kwargs[key]

        self._headerPath = None
        key = 'headerPath'
        if key in self._kwargs:
            self._headerPath = self._kwargs[key]
            del self._kwargs[key]

        self._headerDefinition = None
        key = 'headerDefinition'
        if key in self._kwargs:
            self._headerDefinition = self._kwargs[key]
            del self._kwargs[key]

        self._kind = None
        key = 'kind'
        if key in self._kwargs:
            self._kind = self._kwargs[key]
            del self._kwargs[key]

        self._parentId = None
        key = 'parent'
        if key in self._kwargs:
            self._parentId = self._kwargs[key]
            del self._kwargs[key]

        # ???
        # ---------------------------------------------------------------------
        self._sourcesPathsList = None
        key = 'sourcesPaths'
        if key in self._kwargs:
            self._sourcesPathsList = self._kwargs[key]
            del self._kwargs[key]
        
        return


    # return a string identifying the object (the class name)
    def getObjectType(self):
        
        return self.__class__.__name__
    
    
    # return the dictionary of not recognised keywords
    def getNonRecognisedKeywords(self):
        
        return self._kwargs;
    
    # -------------------------------------------------------------------------
    def setFlavor(self, flavorString):
        
        self._flavor = Flavor.construct(flavorString)
        return
    
    # -------------------------------------------------------------------------
    # main properties id, name, description
    def getId(self):
        
        return self._id
    
    
    def getName(self):
        
        return self._name
    
    
    def getDescription(self):
        
        return self._description
    

    
    # -------------------------------------------------------------------------
    # tree links
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
    
    
    def getTreeChildrenList(self):
        
        return self._treeChildrenList


    # -------------------------------------------------------------------------
    def getParentId(self):
        
        return self._parentId
    
    
    def getCompileList(self):
        
        return self._compileList
        
        
    def getHeaderPath(self):
        
        return self._headerPath
    
    
    def getHeaderDefinition(self):
        
        return self._headerDefinition
    
    
    def getKind(self):
        
        return self._kind
    
    
    def setKind(self, kind):
        
        self._kind = kind
        return
        
    def getPackageLocation(self):
        
        return self._packageLocation
    
    
    def setPackageLocation(self, packageLocation):
        
        self._packageLocation = packageLocation
        return
    
    
    
    def getPackageTreeNode(self):
        
        if self.getObjectType() == 'Package':
            return self
        
        if self._treeParent == None:
            return None
        
        return self._treeParent.getPackageTreeNode()


    # a node is loaded if its parent package is loaded
    def isLoaded(self):
        
        return self.getPackageTreeNode().isLoaded()
    
    
    # -------------------------------------------------------------------------
    # support for simple objects, to avoid additional tests
    
    # simple objects have no children
    def getChildrenList(self):
        
        return None
    

    # simple objects have no scripts
    def getScriptsList(self):
        
        return None
    
    # simple objects have no loadPackages
    def getLoadPackagesList(self):
        
        return None
    

    # ???
    # -------------------------------------------------------------------------
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
    
    
    
    # climb the hierarchy until found
    def getSourcePathsList(self):
        
        # if explicitly set, return it
        if self._sourcesPathsList != None:
            return self._sourcesPathsList
        
        # if there is no parent, then no other chance left
        if self._treeParent == None:
            return None
        
        # return the parent base path
        return self._treeParent.getSourcePathsList()


    