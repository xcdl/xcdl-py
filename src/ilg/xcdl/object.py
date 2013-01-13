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
        self._isConfigurableExpression = None
        if key in self._kwargs:
            self._isConfigurableExpression = self._kwargs[key]
            del self._kwargs[key]

        self.isConfigurable = self.getDefaultIsConfigurable()
        
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
            if val not in ['none', 'bool', 'int', 'float', 'string']:
                print 'ERROR: Unsupported valueType \'{0}\' using \'none\' in node \'{1}\''.format(val, self._id)
            
            self._valueType = self._kwargs[key]
            del self._kwargs[key]
        
        self._value = None
        
        key='valueFormat'
        self._valueFormat = None
        if key in self._kwargs:
            self._valueFormat = self._kwargs[key]
            del self._kwargs[key]
                        
        key='computed'
        self._computedExpression = None
        if key in self._kwargs:
            self._computedExpression = self._kwargs[key]
            del self._kwargs[key]

        key='defaultValue'
        self._defaultValueExpression = None
        if self._computedExpression != None:
            print 'ERROR: Node {0} already has a compute, \‘defaultValue\' ignored'.format(self._id)
        else:
            if key in self._kwargs:
                self._defaultValueExpression = self._kwargs[key]
                del self._kwargs[key]

        key='legalValues'
        self._legalValuesList = None
        if key in self._kwargs:
            self._legalValuesList = self._kwargs[key]
            del self._kwargs[key]
            
        key='activeIf'
        self._activeIfList = None
        if key in self._kwargs:
            self._activeIfList = self.enforceListOfStrings(self._kwargs[key], self._id, key)
            del self._kwargs[key]

        key='requires'
        self._requiresList = None
        if key in self._kwargs:
            self._requiresList = self.enforceListOfStrings(self._kwargs[key], self._id, key)
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
   
   
    def enforceListOfStrings(self, args, sid, key):
        
        if isinstance(args, basestring):
            localList = []
            localList.append(args)
            return localList
        elif isinstance(args, list):
            localList = []
            for arg in args:
                if isinstance(arg, basestring):
                    localList.append(arg)
                else:
                    print 'ERROR: \'{0}\' value \'{1}\' not a string in node \'{2}\''.format(key, arg, sid)
            if len(localList) > 0:
                return localList
        return None

        
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
    

    def getDefaultIsConfigurable(self):
        
        # most objects start as configurable (interfaces are exceptions)
        return True
    
    # return True if the value was set
    def setIsEnabled(self, isEnabled = True):

        if not self.isLoaded():
            return False
        
        self._isEnabled = isEnabled
        return True


    # return 1 if the value was changed
    def setIsEnabledWithCount(self, isEnabled = True):

        if not self.isLoaded():
            return 0
        
        count = 1 if (self._isEnabled != isEnabled) else 0
        self._isEnabled = isEnabled
        return count


    def getValueType(self):
        
        return self._valueType

    
    def getValueTypeWithDefault(self):
        
        if self._valueType != None:
            return self._valueType
        
        return 'none'
        

    # return the object's value, with the type as it resulted from evaluation
    def getValue(self):

        if not self.isActive():
            return 0
        
        valueType = self.getValueTypeWithDefault()
        if valueType != 'none':

            # give priority to computed expressions
            if self._computedExpression != None:
                return self._evaluateExpression(self._computedExpression)
    
            if self._value != None:
                return self._evaluateExpression(self._value)
    
            if self._defaultValueExpression != None:
                return self._evaluateExpression(self._defaultValueExpression)
    
        # otherwise active objects have a value of 1/True
        return 1


    # return the object's value according to the valueType
    def getValueWithType(self):
        
        value = self.getValue()
        
        valueString = str(value)
        valueType = self.getValueTypeWithDefault()
        
        if valueType == 'bool':
            return (True if (valueString == '1' or valueString == 'True') else False)
        elif valueType == 'string':
            return valueString
        elif valueType == 'int':
            return int(valueString)
        elif valueType == 'float':
            return float(valueString)
        else:
            return value
        
    
    def setValueWithCount(self, value):
        
        evaluatedValue = self._evaluateExpression(value)
        
        # TODO: check limits
        
        count = 0
        if evaluatedValue != None:
            if self._value != evaluatedValue:  
                self._value = evaluatedValue
                count = 1
        
        return count


    def _evaluateExpression(self, expression):
        
        if isinstance(expression, basestring):
            expression = expression.strip()
        
        evaluatedValue = None
        valueType = self.getValueTypeWithDefault()
        if valueType == 'none':    
            return None
        elif valueType == 'string':
            if isinstance(expression, basestring):
                try:
                    evaluatedValue = eval(expression)
                except:
                    evaluatedValue = expression
            else:
                evaluatedValue = str(expression)
        elif valueType == 'bool':
            if isinstance(expression, basestring):
                try:
                    evaluatedValue = eval(expression)
                except:
                    evaluatedValue = True if (expression.lower() == 'true') else False
            else:
                evaluatedValue = True if expression else False
        elif valueType == 'int':
            if isinstance(expression, basestring):
                try:
                    evaluatedValue = int(eval(expression))
                except:
                    try:
                        evaluatedValue = int(expression)
                    except:
                        print 'ERROR: string expression \'{0}\' not integer, in node \'{1}\' (use 0)'.format(expression, self._id)
                        evaluatedValue = 0
            else:
                try:
                    evaluatedValue = int(expression)
                except:
                    print 'ERROR: expression \'{0}\' not integer, in node \'{1}\' (use 0)'.format(expression, self._id)
                    evaluatedValue = 0
                    
        elif valueType == 'float':
            if isinstance(expression, basestring):
                try:
                    evaluatedValue = float(eval(expression))
                except:
                    try:
                        evaluatedValue = float(expression)
                    except:
                        print 'ERROR: string expression \'{0}\' not float, in node \'{1}\' (use 0)'.format(expression, self._id)
                        evaluatedValue = 0.0                        
            else:
                try:
                    evaluatedValue = float(expression)
                except:
                    print 'ERROR: expression \'{0}\' not float, in node \'{1}\' (use 0)'.format(expression, self._id)
                    evaluatedValue = 0
        
        return evaluatedValue 
        
    
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
    
    
    def getRequiresList(self):
        
        return self._requiresList
    
    
    def isConfigurableEvaluated(self):
        
        if self._isConfigurableExpression == None:
            return self.getDefaultIsConfigurable()
        
        if isinstance(self._isConfigurableExpression, basestring):            
            return eval(self._isConfigurableExpression)
        else:
            return self._isConfigurableExpression
        
    
