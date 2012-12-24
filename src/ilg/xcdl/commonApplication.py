# -*- coding: utf-8 -*-

import os

from ilg.xcdl.errorWithDescription import ErrorWithDescription
from ilg.xcdl.object import Object

from ilg.xcdl.packageLocation import PackageLocation

# WARNING: DO NOT REMOVE!
# the following are needed in executed scripts
from ilg.xcdl.component import Component  # @UnusedImport
from ilg.xcdl.package import Package  # @UnusedImport
from ilg.xcdl.configuration import Configuration  # @UnusedImport


class CommonApplication(object):

    def __init__(self, *argv):
        
        self.argv = argv
        
        self.isVerbose = False

        # initialise the dictionary where all objects will be stored
        self.allObjectsDict = {}

        self.defaultScripts = ['meta/xcdl.py']
        
        return
    
    
    def loadPackagesTrees(self, packagesFilePathList):
        
        # build a list of trees, for all given packages
        packagesTreesList = []
                
        for filePath in packagesFilePathList:
            
            packsList = self.loadPackageTree(filePath)
            if packsList != None:
                packagesTreesList.extend(packsList)
        
        return packagesTreesList
    

    def loadPackageTree(self, packagePath):
                        
        packageAbsolutePath = os.path.abspath(packagePath)

        if os.path.isdir(packageAbsolutePath):
            print 'Process package folder {0}'.format(packagePath)
            rootList = self.recurseProcessFolder(None, packageAbsolutePath)
        elif os.path.isfile(packagePath):
            print 'Process package file {0}'.format(packagePath)
            # process the given script and recurse
            rootList = self.processScript(None, packageAbsolutePath)
        else:
            raise ErrorWithDescription("Path not a folder or a file")
            
        return rootList


    def loadConfig(self, configFilePath):
                
        print 'Process configuration file \'{0}\''.format(configFilePath)
        configFileAbsolutePath = os.path.abspath(self.configFilePath)
        
        # process the given script and recurse
        rootList = self.processScript(None, configFileAbsolutePath, None)
        return rootList
    
    
    def recurseProcessFolder(self, parent, folderAbsolutePath):
        
        crtParent = parent
        localList = []
        for path in self.defaultScripts:
            tentativeFileAbsolutePath = os.path.join(folderAbsolutePath, path)
            if os.path.isfile(tentativeFileAbsolutePath):
                if self.isVerbose:
                    print 'is package'
                
                packageLocation = PackageLocation(folderAbsolutePath, tentativeFileAbsolutePath)
                localList = self.processScript(parent, tentativeFileAbsolutePath, packageLocation)
                crtParent = localList[0]
                break
                 
        for name in os.listdir(folderAbsolutePath):
            absolutePath = os.path.join(folderAbsolutePath, name)
            if os.path.isdir(absolutePath):
                if self.isVerbose:
                    print 'subfolder {0}'.format(absolutePath)
                self.recurseProcessFolder(crtParent, absolutePath)
        
        return localList
    
    
    def processScript(self, parent, scriptAbsolutePath, packageLocation):
        
        if self.isVerbose:
            print 'process script {0}'.format(scriptAbsolutePath)
        
        # list used to collect all objects contributed by encountered 
        # constructors
        localList = []
        Object.setList(localList)
        
        if not os.path.isfile(scriptAbsolutePath):
            raise ErrorWithDescription('Missing script file \'{0}\''.
                                       format(scriptAbsolutePath))

        execfile(scriptAbsolutePath)
        
        self.warnNonParsedKeywords(localList)
        
        # manual links to children or to parent
        localList = self.linkChildrenNodes(localList)
        localList = self.linkNodesWithParent(localList)
        
        # process parsed nodes
        for obj in localList:            
            self.processNode(obj, parent, scriptAbsolutePath, packageLocation)
            
        # return the current list, useful for the root node,
        # all other use the parent to build the tree                    
        return localList


    def warnNonParsedKeywords(self, localList):

        for node in localList:            

            # warn if some of the keywords were not parsed
            if len(node.getNonParsedKeywords()) > 0:
                print 'Ignored keywords {0} in {1}'.format(
                        node.getNonParsedKeywords(), node.getId())
        
        return
        

    def linkChildrenNodes(self, localList):
                
        for node in localList:
            
            if node.getChildrenList() == None:
                continue
                
            # print 'has children {0}'.format(node.getId())
            for child in node.getChildrenList():
                # print 'child {0}'.format(child.getId())
                
                # link-up to parent
                child.setTreeParent(node)
                # link-down to child
                node.addTreeChild(child)
            
        shortList = []
        for node in localList:
            
            # non-linked nodes will be processed further
            if node.getTreeParent() == None:
                shortList.append(node)
                        
        return shortList
    

    def linkNodesWithParent(self, localList):
        
        oldList = localList
        while True:
            
            newList = []
            
            for node in oldList:
                
                parentName = node.getParentName()
                if parentName == None:
                    newList.append(node)
                    continue
                
                # this node has a parent definition
                
                found = False
                for parentNode in oldList:                    
                    if parentName == parentNode.getId():
                        found = True
                        break
                    
                # if it's parent is not know, continue                
                if not found:
                    newList.append(node)
                    continue                    
                
                # if the node parent is known, link to it
                node.setTreeParent(parentNode)
                parentNode.addTreeChild(node)
                # do not pass it to new list
            
            if len(oldList) == len(newList):
                break
            
            oldList = newList
            
        return newList
    
    
    def processNode(self, node, parent, scriptAbsolutePath, packageLocation):
          
        # check if the name was already used
        if node.getId() in self.allObjectsDict:
                
            oldObject = self.allObjectsDict[node.getId()]
            oldKind = oldObject.getObjectType()
            oldName = oldObject.getName()
            oldDescription = oldObject.getDescription()
            
            if (oldName == node.getName()) and (oldDescription == node.getDescription()):
                return
            
            raise ErrorWithDescription('Name {0} \'{1}\' redefined (was {2} \'{3}\''.
                            format(node.getId(), node.getName(), oldKind, oldName))
              
        # eventually process local parent
        parentName = node.getParentName()
        if parentName != None and parent != None:
            if parent.getId() != parentName:
                print 'Parent of {0} already is {1}, redefined as {2}, ignored'.format(
                                node.getId(), parent.getId(), parentName)
            parentName = None
            
        if parentName != None:
            
            # compute parent object from parent name
            if parentName not in self.allObjectsDict:
                # TODO: check if possible to use a deferred list
                raise ErrorWithDescription('Parent {0} not defined'.
                                               format(parentName))
                    
            crtParent = self.allObjectsDict[parentName]
        else:
            crtParent = parent

        if node.getTreeParent() == None:
            
            # up-link from the current object to the given parent
            node.setTreeParent(crtParent)
            
            # down-link from the parent to the current object
            if crtParent != None:
                crtParent.addTreeChild(node)

        # remember the current package location
        if node.getPackageLocation() == None:
            node.setPackageLocation(packageLocation)
            
        # store current object in the global dictionary    
        self.allObjectsDict[node.getId()] = node
        
        # process inner scripts        
        scriptsList = node.getScripts()
        if scriptsList != None:
                
            baseRelativePath = node.getBasePath()
            (scriptAbsoluteFolder, _) = os.path.split(scriptAbsolutePath)
            baseAbsolutePath = os.path.abspath(os.path.join(
                                        scriptAbsoluteFolder, baseRelativePath))
                                
            for child in scriptsList:
                    
                # print child
                childAbsolutePath = os.path.abspath(os.path.join(
                                                baseAbsolutePath, child))
                # print childAbsolutePath
                    
                self.processScript(node, childAbsolutePath, packageLocation)
                
        
        # process children nodes recursively
        childrenList = node.getChildrenList()
        if childrenList != None:
            
            for child in childrenList:
                self.processNode(child, node, scriptAbsolutePath, packageLocation)
                
        return
    
    
    def dumpTree(self, packagesTreesList):
        
        print "The packages trees:"
        print
        for tree in packagesTreesList:
            self.recurseDumpTree(tree, 0)
        return
    
        
    def recurseDumpTree(self, node, depth):
        
        indent = '   '
        
        kind = None
        if node.getObjectType() != None:
            kind = ' ({0}'.format(node.getObjectType())
            if node.getKind() != None:
                kind += ',{0}'.format(node.getKind())
            kind += ')'
            
        print '{0}* {1} \'{2}\'{3}'.format(indent * depth, node.getId(),
                            node.getName(), kind)

        packageLocation = node.getPackageLocation()
        if packageLocation != None:
            print '{0}- packageFolder {1}'.format(indent * (depth + 1),
                                    packageLocation.getFolderAbsolutePath())
            
        # dump sources, if any
        sourcesList = node.getCompileList()
        if sourcesList != None:
            for source in sourcesList:
                print '{0}- compile {1}'.format(indent * (depth + 1), source)

        # dump sources, if any
        enableList = node.getEnableList()
        if enableList != None:
            for enable in enableList:
                print '{0}- enable {1}'.format(indent * (depth + 1), enable)
                
        children = node.getTreeChildrenList()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.recurseDumpTree(child, depth + 1)            
            
        return

    
    def dumpConfiguration(self, configTreesList):
        
        print "The configuration trees:"
        print
        for tree in configTreesList:
            self.recurseDumpConfiguration(tree, 0)
        return
    
        
    def recurseDumpConfiguration(self, node, depth):
        
        indent = '   '
        
        kind = None
        if node.getObjectType() != None:
            kind = ' ({0})'.format(node.getObjectType())
            
        print '{0}* {1} \'{2}\'{3}'.format(indent * depth, node.getId(),
                            node.getName(), kind)

        # dump sources, if any
        requiresList = node.getEnableList()
        if requiresList != None and len(requiresList) > 0:
            for requires in requiresList:
                print '{0}- requires {1}'.format(indent * (depth + 1), requires)
        
        optionsList = node.getOptions()
        if optionsList != None and len(optionsList) > 0:
            for key in optionsList.keys():
                print'{0}- option {1}={2}'.format(indent * (depth + 1), key,
                                                  optionsList[key])
                     
        buildFolder = node.getBuildFolder()
        if buildFolder != None:
            print'{0}- buildFolder=\'{1}\''.format(indent * (depth + 1), buildFolder)

        preprocessorSymbols = node.getPreprocessorSymbols()
        if preprocessorSymbols != None:
            for preprocessorSymbol in preprocessorSymbols:
                print '{0}- preprocessorSymbol=\'{1}\''.format(indent * (depth + 1),
                                                            preprocessorSymbol)
                    
        children = node.getTreeChildrenList()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.recurseDumpConfiguration(child, depth + 1)
                        
        return

    
    def enableConfiguration(self, configTreesList, sid):
        
        print 'Enable configuration {0}'.format(sid)
        print
        
        if sid not in self.allObjectsDict:
            print 'Missing id, cancelled'
            return
        
        configNode = self.allObjectsDict[sid]
        
        self.enableConfigNode(configNode)
        return
    
    
    def enableConfigNode(self, configNode):
        
        if configNode.getObjectType() != 'configuration':
            raise ErrorWithDescription('Not a configuration node {0}'.format(configNode.getName()))
        
        if self.isVerbose:
            print 'enable {0}'.format(configNode.getId())

        enableList = configNode.getEnableList()
        if enableList != None:
            for enable in enableList:
                self.enableTreeNode(enable)
        
        treeParent = configNode.getTreeParent()
        if treeParent != None:
            self.enableConfigNode(treeParent)
               
        return
    
                
    def enableTreeNode(self, treeNodeId):

        if treeNodeId not in self.allObjectsDict:
            raise ErrorWithDescription('Missing enebled node {0}'.format(treeNodeId))
        
        treeNode = self.allObjectsDict[treeNodeId]
        if treeNode.getObjectType() not in [ 'component', 'option' ]:
            raise ErrorWithDescription('Not a package node {0}'.format(treeNode.getName()))
        
        if self.isVerbose:
            print 'enable {0}'.format(treeNodeId)
            
        treeNode.setIsEnabled()
        
        enableList = treeNode.getEnableList()
        if enableList != None:
            for enable in enableList:
                self.enableTreeNode(enable)
                
        return
    
    
        

    
