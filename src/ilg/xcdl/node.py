# -*- coding: utf-8 -*-

from ilg.xcdl.errorWithDescription import ErrorWithDescription
#from ilg.xcdl.commonApplication import evaluateExpression
import ilg.xcdl.commonApplication

class Node(object):
    
    # static member
    _objectsList = None

    
    @staticmethod
    def setList(oList):
        
        Node._objectsList = oList
        return


    @staticmethod    
    def getList():
        
        return Node._objectsList
    
    
    def __init__(self, **kwargs):
        
        # store the current keywords args dictionary. 
        # will be consumed on each constructor
        self._kwargs = kwargs

        # ---------------------------------------------------------------------
        try:
            if 'id' in kwargs:
                obj = 'id={0}'.format(kwargs['id'])
            else:
                obj = kwargs
                
            for key in self.unavailableKeywords:
                if key in self._kwargs:
                    print 'Property {0} unavailable for object {1}, ignored'.format(key, obj)
                    del self._kwargs[key]
        except:
            pass
        

        # if the static list is defined, add object to the list
        if Node._objectsList != None:
            Node._objectsList.append(self)

        # initialise empty members
        self._treeParent = None
        self._treeChildrenList = None
        self._basePath = None        
        self._packageLocation = None

        # can be set only in Repository object
        self._sourcesPathsList = None
        
        # the file where this node is located
        self._scriptAbsolutePath = None

        self._copyFilesList = None

        self._wasProcessed = False
        
        # ---------------------------------------------------------------------
        self._isEnabled = self.getDefaultIsEnabled()
        
        # ---------------------------------------------------------------------
        # main properties id, name, description

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
        else:
            raise ErrorWithDescription('Mandatory name missing, id=\'{0}\''.format(self._id))

        key = 'description'
        self._description = None
        if key in self._kwargs:
            self._description = self._kwargs[key]
            del self._kwargs[key]
        else:
            raise ErrorWithDescription('Mandatory description missing, id=\'{0}\''.format(self._id))
                
        # ---------------------------------------------------------------------
        # hierarchy related properties

        key = 'parent'
        self._parentId = None
        if key in self._kwargs:
            self._parentId = self._kwargs[key]
            del self._kwargs[key]

        # ---------------------------------------------------------------------
        # grouping

        key = 'category'
        self._category = None
        if key in self._kwargs:
            self._category = self._kwargs[key]
            del self._kwargs[key]

        # ---------------------------------------------------------------------
        # other?
        
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
    def getParentId(self):
        
        return self._parentId
    
    
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
        
        if self.getObjectType() == 'Package' or self.getObjectType() == 'Repository':
            return self
        
        if self._treeParent == None:
            return None
        
        return self._treeParent.getPackageTreeNode()

    # -------------------------------------------------------------------------

    def setScriptAbsolutePath(self, absolutePath):
        
        self._scriptAbsolutePath = absolutePath
        return


    def getScriptAbsolutePath(self):
        
        return self._scriptAbsolutePath

    # -------------------------------------------------------------------------
    # a node is loaded if its parent package is loaded

    def isLoaded(self):
        
        return self.getPackageTreeNode().isLoaded()
    
    # -------------------------------------------------------------------------
    def isEnabled(self):
        
        # nodes need to be loaded to be enabled
        if not self.isLoaded():
            return False

        # nodes need to have their parents enabled to be enabled
        if self._treeParent != None:
            if not self._treeParent.isEnabled():
                return False
            
        return self._isEnabled

    
    # return True if the value was set
    def setIsEnabled(self, isEnabled=True):

        if not self.isLoaded():
            return False
        
        self._isEnabled = isEnabled
        return True


    # return 1 if the value was changed
    def setIsEnabledWithCount(self, isEnabled=True):

        if not self.isLoaded():
            return 0
        
        count = 1 if (self._isEnabled != isEnabled) else 0
        self._isEnabled = isEnabled
        return count

    def setIsEnabledWithCountRecursive(self, isEnabled=True):

        if not self.isLoaded():
            return 0
        
        count = 1 if (self._isEnabled != isEnabled) else 0
        self._isEnabled = isEnabled
        
        if self._treeParent != None:
            count += self._treeParent.setIsEnabledWithCountRecursive()

        return count


    # -------------------------------------------------------------------------
    # support for simple objects, to avoid additional tests
        
    def isActive(self):
        
        return False
    
    
    # simple objects have no children
    def getChildrenList(self):
        
        return None
    

    # simple objects have no scripts
    def getIncludesList(self):
        
        return None
    
    # simple objects have no loadPackages
    def getLoadPackagesList(self):
        
        return None


    def getInitialIsEnabled(self):
        
        return False
    
    
    def getDefaultIsEnabled(self):
        
        # most objects start as enabled
        # overwrite this for objects that are exceptions to this rule
        return True
    

    def getDefaultIsConfigurable(self):
        
        # most objects start as configurable (interfaces are exceptions)
        return True


    def getHeaderDefinition(self):
        
        return None


    def getHeaderLineAndFileName(self):
        
        return None

    def getSourceFilesList(self):
        
        return None

    def getImplementsList(self):
        
        return None

    def getChildrenHeaderFile(self):
        
        return None

    # -------------------------------------------------------------------------

    def wasProcessed(self):
        
        return self._wasProcessed
    
    
    def setWasProcessed(self):
        
        self._wasProcessed = True
        
        
    # -------------------------------------------------------------------------
    def getCopyFilesList(self):
        
        return self._copyFilesList
    

    # -------------------------------------------------------------------------
    def getRepositoryFolderAbsolutePath(self):
        
        # the Repository node will terminate the recursion
        return self._treeParent.getRepositoryFolderAbsolutePath()
            
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
    


# -----------------------------------------------------------------------------

class ActiveNode(Node):

    def __init__(self, **kwargs):
        
        super(ActiveNode, self).__init__(**kwargs)
        
        # ---------------------------------------------------------------------
        # build related properties

        key = 'sourceFiles'
        self._sourceFilesList = None
        if key in self._kwargs:
            self._sourceFilesList = self._kwargs[key]
            del self._kwargs[key]

        key = 'linkPriority'
        self._linkPriority = None
        if key in self._kwargs:
            if self._sourceFilesList == None or len(self._sourceFilesList) == 0:
                print 'ERROR: Node {0} has no source files, \'linkPriority\' ignored'.format(self._id)
            else:
                try:
                    n = int(self._kwargs[key])
                    if 0 <= n and n <= 99:
                        self._linkPriority = n
                    else:
                        print 'ERROR: \'linkPriority\' not in [00-99], ignored, Node {0}'.format(self._id)
                except:
                    print 'ERROR: \'linkPriority\' not a number, ignored, Node {0}'.format(self._id)
                                    
            del self._kwargs[key]


        # ---------------------------------------------------------------------
        # status properties
            
        key = 'isConfigurable'
        self._isConfigurableExpression = None
        if key in self._kwargs:
            self._isConfigurableExpression = self._kwargs[key]
            del self._kwargs[key]

        
        self._isEnabled = self.getDefaultIsEnabled()

        key = 'isEnabled'
        self._initialIsEnabled = None
        if key in self._kwargs:
            self._initialIsEnabled = self._kwargs[key]
            del self._kwargs[key]
            
            # if the value is a constant, apply it here
            if isinstance(self._initialIsEnabled, bool):
                self._isEnabled = self._initialIsEnabled

        # ---------------------------------------------------------------------
        # value related properties
        
        key = 'valueType'
        self._valueType = None
        if key in self._kwargs:
            # none, bool, number, string
            val = self._kwargs[key]
            if val not in ['none', 'bool', 'int', 'float', 'string']:
                print 'ERROR: Unsupported valueType \'{0}\', defaulting to \'none\' in node \'{1}\''.format(val, self._id)
                self._valueType = 'none'
            else:
                self._valueType = self._kwargs[key]
            del self._kwargs[key]
        
        self._value = None
        
        key = 'computed'
        self._computedExpression = None
        if key in self._kwargs:
            if self._valueType == None or self._valueType == 'none':
                print 'ERROR: Node {0} has no value, \'computed\' ignored'.format(self._id)
            else:
                self._computedExpression = self._kwargs[key]
                
            del self._kwargs[key]

        key = 'defaultValue'
        self._defaultValueExpression = None
        if key in self._kwargs:
            if self._computedExpression != None:
                print 'ERROR: Node {0} already has a compute, \'defaultValue={1}\' ignored'.format(self._id, self._kwargs[key])
            else:
                if self._valueType == None or self._valueType == 'none':
                    print 'ERROR: Node {0} has no value, \'defaultValue={1}\' ignored'.format(self._id, self._kwargs[key])
                else:
                    self._defaultValueExpression = self._kwargs[key]
                
            del self._kwargs[key]

        key = 'legalValues'
        self._legalValuesList = None
        if key in self._kwargs:
            if self._valueType == None or self._valueType == 'none':
                print 'ERROR: Node {0} has no value, \'legalValues\' ignored'.format(self._id)
            else:
                self._legalValuesList = self._kwargs[key]
                
            del self._kwargs[key]

        key = 'valueFormat'
        self._valueFormat = None
        if key in self._kwargs:
            self._valueFormat = self._kwargs[key]
            del self._kwargs[key]
                                    
        # ---------------------------------------------------------------------
        # constraints related properties

        key = 'activeIf'
        self._activeIfList = None
        if key in self._kwargs:
            self._activeIfList = self.enforceListOfStrings(self._kwargs[key], self._id, key)
            del self._kwargs[key]

        key = 'requirements'
        self._requiresList = None
        if key in self._kwargs:
            self._requiresList = self.enforceListOfStrings(self._kwargs[key], self._id, key)
            del self._kwargs[key]

        key = 'implements'
        self._implementsList = None
        if key in self._kwargs:
            self._implementsList = self._kwargs[key]
            del self._kwargs[key]

        key = 'copyFiles'
        self._copyFilesList = None
        if key in self._kwargs:
            self._copyFilesList = self._kwargs[key]
            del self._kwargs[key]
            
        # ---------------------------------------------------------------------
        # header related properties

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

        return
    
    
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

    def getValueIfAny(self):

        if not self.isActive():
            return None
        
        if self._computedExpression == None and self._value == None and self._defaultValueExpression == None:
            return None

        valueType = self.getValueTypeWithDefault()
        if valueType != 'none':

            
            # give priority to computed expressions
            if self._computedExpression != None:
                return ilg.xcdl.commonApplication.evaluateExpression(self._computedExpression, self)
    
            if self._value != None:
                return ilg.xcdl.commonApplication.evaluateExpression(self._value, self)
    
            if self._defaultValueExpression != None:
                return ilg.xcdl.commonApplication.evaluateExpression(self._defaultValueExpression, self)
    
        # otherwise active objects have a value of 1/True
        return None


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

    def getValueIfAnyWithType(self):
        
        valueType = self.getValueTypeWithDefault()
        
        if valueType == 'none':
            # non typed options should always be generated
            return self.getValue()
        
        # typed option are generated only if they have content
        value = self.getValueIfAny()
        if value == None:
            return None
        
        valueString = str(value)

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
                    except Exception as err:
                        print str(err)
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
    def getSourceFilesList(self):
        
        return self._sourceFilesList
        
        
    def getHeaderFile(self):
        
        return self._headerFile
    

    def getHeaderFileRecursive(self):
        
        if self._headerFile != None:
            return self._headerFile
        
        if self._treeParent != None:
            
            headerFile = self._treeParent.getChildrenHeaderFile()
            if headerFile != None:
                return headerFile
            
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
        
        formattedValue = self.getFormattedValueIfAny()
        if formattedValue == None:
            return None
        
        headerLine = '#define    {0}    {1}'.format(headerDefinition, formattedValue)

        headerFile = self.getHeaderFileRecursive()
        if headerFile == None:
            return None
        
        return (headerLine, headerFile)


    

    def getImplementsList(self):
        
        return self._implementsList
    
        
    def computeSingleActiveIf(self, activeIf):
        
        #print 'computeSingleActiveIf({0})'.format(activeIf)
        
        # TODO: accept expressions too
        sid = activeIf
        return ilg.xcdl.commonApplication.isActive(sid)


#    def computeSingleRequires(self, requires):
#        
#        print 'computeSingleRequires({0})'.format(requires)
#        
#        # TODO: implement
#        return True

        
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


    # used to generate #define lines
    def getFormattedValue(self):
        
        formatString = self.getValueFormatWithDefault()
        valueWithType = self.getValueWithType()
        #valueWithType = self.getValueAsString()
        if isinstance(valueWithType, bool):
            valueWithType = str(valueWithType).lower()
        
        return formatString.format(valueWithType)

    def getFormattedValueIfAny(self):
        
        formatString = self.getValueFormatWithDefault()
        valueWithType = self.getValueIfAnyWithType()
        if valueWithType == None:
            return None
        
        #valueWithType = self.getValueAsString()
        if isinstance(valueWithType, bool):
            valueWithType = str(valueWithType).lower()
        
        return formatString.format(valueWithType)
    
    
    def getRequiresList(self):
        
        return self._requiresList

    
    def getInitialIsEnabled(self):
        
        return self._initialIsEnabled
    
    
    def isConfigurableEvaluated(self):
        
        if self._isConfigurableExpression == None:
            return self.getDefaultIsConfigurable()
        
        if isinstance(self._isConfigurableExpression, basestring):            
            return eval(self._isConfigurableExpression)
        else:
            return True if self._isConfigurableExpression else False

        
    def getLinkPriority(self):
        
        return self._linkPriority
    

