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

        # if the static list is defined, add object to the list
        if Object._objectsList != None:
            Object._objectsList.append(self)

        # initialise empty members
        self._treeParent = None
        self._treeChildrenList = None
        self._basePath = None        
        self._packageLocation = None
        
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
            
        key = 'name'
        self._name = None        
        if key in self._kwargs:
            self._name = self._kwargs[key]
            del self._kwargs[key]

        key = 'description'
        self._description = None
        if key in self._kwargs:
            self._description = self._kwargs[key]
            del self._kwargs[key]
                
        key = 'sourceFiles'
        self._sourceFilesList = None
        if key in self._kwargs:
            self._sourceFilesList = self._kwargs[key]
            del self._kwargs[key]

        # ---------------------------------------------------------------------
            
        key='isConfigurable'
        self._isConfigurable = None
        if key in self._kwargs:
            self._isConfigurable = self._kwargs[key]
            del self._kwargs[key]

        key='isEnabled'
        self._initialIsEnabled = None
        if key in self._kwargs:
            self._initialIsEnabled = self._kwargs[key]
            del self._kwargs[key]
            
        self._isEnabled = self.getDefaultIsEnabled()

        key='valueType'
        self._valueType = None
        if key in self._kwargs:
            # none, bool, number, string
            val = self._kwargs[key]
            if val not in ['none', 'bool', 'number', 'string']:
                raise ErrorWithDescription('Unsupported valueType {0}'.format(val))
            
            self._valueType = self._kwargs[key]
            del self._kwargs[key]
        
        self._value = None
        
        key='valueFormat'
        self._valueFormat = None
        if key in self._kwargs:
            self._valueFormat = self._kwargs[key]
            del self._kwargs[key]
                        
        key='computed'
        self._computed = None
        if key in self._kwargs:
            self._computed = self._kwargs[key]
            del self._kwargs[key]

        key='defaultValue'
        self._defaultValue = None
        if self._computed != None:
            print 'Node {0} already has a compute, \‘defaultValue\' ignored'.format(self._id)
        else:
            if key in self._kwargs:
                self._defaultValue = self._kwargs[key]
                del self._kwargs[key]

        key='legalValues'
        self._legalValuesList = None
        if key in self._kwargs:
            self._legalValuesList = self._kwargs[key]
            del self._kwargs[key]
            
        key='activeIf'
        self._activeIfList = None
        if key in self._kwargs:
            self._activeIfList = self._kwargs[key]
            del self._kwargs[key]

        key='requires'
        self._requiresList = None
        if key in self._kwargs:
            self._requiresList = self._kwargs[key]
            del self._kwargs[key]

        key='implements'
        self._implementsList = None
        if key in self._kwargs:
            self._implementsList = self._kwargs[key]
            del self._kwargs[key]
            
        # ---------------------------------------------------------------------

        key = 'headerFile'
        self._headerFile = None
        if key in self._kwargs:
            self._headerFile = self._kwargs[key]
            del self._kwargs[key]

        key = 'headerDefinition'
        self._headerDefinition = None
        if key in self._kwargs:
            self._headerDefinition = self._kwargs[key]
            del self._kwargs[key]

        # ---------------------------------------------------------------------

        key = 'category'
        self._category = None
        if key in self._kwargs:
            self._category = self._kwargs[key]
            del self._kwargs[key]

        key = 'parent'
        self._parentId = None
        if key in self._kwargs:
            self._parentId = self._kwargs[key]
            del self._kwargs[key]

        # ???
        # ---------------------------------------------------------------------
        key = 'sourcesPaths'
        self._sourcesPathsList = None
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
    
    
    # get the root of the current tree
    def getTreeRoot(self):
        
        if self._treeParent == None:
            return self
        
        return self._treeParent.getTreeRoot()
    
    
    def addTreeChild(self, child):
        
        if self._treeChildrenList == None:
            self._treeChildrenList = []
            
        self._treeChildrenList.append(child)
        
        return
    
    
    def getTreeChildrenList(self):
        
        return self._treeChildrenList


    # -------------------------------------------------------------------------

    def isActive(self):
        
        # nodes need to be enabled to be active
        if not self.isEnabled():
            return False
        
        if self._treeParent != None:
            if not self._treeParent.isActive():
                return False
            
        if self._activeIfList != None:
            for activeIf in self._activeIfList:
                if not self.computeSingleActiveIf(activeIf):
                    return False
                pass
        
        return True
    
    
    def isEnabled(self):
        
        # nodes need to be loaded to be enabled
        if not self.isLoaded():
            return False

        # nodes need to have their parents enabled to be enabled
        if self._treeParent != None:
            if not self._treeParent.isEnabled():
                return False
            
        return self._isEnabled


    def getInitialIsEnabled(self):
        
        return self._initialIsEnabled
    
    
    def getDefaultIsEnabled(self):
        
        # most objects start as disabled (packages and interfaces are exceptions)
        return False
    
    
    # return True if the value was set
    def setIsEnabled(self, isEnabled = True):

        if not self.isLoaded():
            return False
        
        self._isEnabled = isEnabled
        return True


    def getValueTypeWithDefault(self):
        
        if self._valueType != None:
            return self._valueType
        
        return 'none'
        

    # return the object's value, with the type as it resulted from evaluation
    def getValue(self):

        if not self.isActive():
            return 0
        
        if self._value != None:
            if isinstance(self._value, basestring):
                return eval(self._value)
            else:
                return self._value
    
        if self._computed != None:
            if isinstance(self._computed, basestring):
                return eval(self._computed)
            else:
                return self._computed

        if self._defaultValue != None:
            if isinstance(self._defaultValue, basestring):
                #return eval(self._defaultValue)
                try:
                    evaluatedValue = eval(self._defaultValue)
                except:
                    evaluatedValue = self._defaultValue
                return evaluatedValue
            else:
                return self._defaultValue
    
        # otherwise active objects have a value of 1/True
        return 1


    # return the object's value according to the valueType
    def getValueWithType(self):
        
        value = self.getValue()
        
        valueString = str(value)
        valueType = self.getValueTypeWithDefault()
        
        if valueType == 'bool':
            return (True if (valueString == '1') else False)
        elif valueType == 'string':
            return valueString
        else:
            floatValue = float(value)
            if float.is_integer(floatValue):
                return int(value)
            else:
                return floatValue
        
    
    # -------------------------------------------------------------------------
    def getParentId(self):
        
        return self._parentId
    
    
    def getSourceFilesList(self):
        
        return self._sourceFilesList
        
        
    def getHeaderFile(self):
        
        return self._headerFile
    

    def getHeaderFileRecursive(self):
        
        if self._headerFile != None:
            return self._headerFile
        
        if self._treeParent != None:
            return self._treeParent.getHeaderFileRecursive()
        
        return None
    
    
    def getHeaderDefinition(self):
        
        return self._headerDefinition

    
    def getHeaderLineAndFileName(self):
        
        headerDefinition = self.getHeaderDefinition()
        if headerDefinition == None:
            return None

        if not self.isActive():
            return None
        
        formattedValue = self.getFormattedValue()
        headerLine = '#define    {0}    {1}'.format(headerDefinition, formattedValue)

        headerFile = self.getHeaderFileRecursive()
        if headerFile == None:
            return None
        
        return (headerLine, headerFile)


    # category='<string>'
    def getCategory(self):
        
        return self._category
    
    
    def setCategory(self, category):
        
        self._category = category
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
    def getIncludesList(self):
        
        return None
    
    # simple objects have no loadPackages
    def getLoadPackagesList(self):
        
        return None

    
    def computeSingleActiveIf(self, activeIf):
        
        return True
    

    def computeSingleRequires(self, requires):
        
        return True
    
    
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
    def getSourcePathsListRecursive(self):
        
        # if explicitly set, return it
        if self._sourcesPathsList != None:
            return self._sourcesPathsList
        
        # if there is no parent, then no other chance left
        if self._treeParent == None:
            return None
        
        # return the parent base path
        return self._treeParent.getSourcePathsListRecursive()


    def getValueFormatWithDefault(self):
        
        # if there is a format defined, return it
        if self._valueFormat != None:
            return self._valueFormat
        
        # otherwise synthesise one
        if self._valueType != None and self._valueType == 'string':
            return '"{0}"'
        else:
            return '({0})'


    def getFormattedValue(self):
        
        formatString = self.getValueFormatWithDefault()
        valueWithType = self.getValueWithType()

        return formatString.format(valueWithType)