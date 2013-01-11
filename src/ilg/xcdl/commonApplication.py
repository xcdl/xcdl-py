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
from ilg.xcdl.interface import Interface  # @UnusedImport
from ilg.xcdl.option import Option  # @UnusedImport

from ilg.xcdl.packageFolder import PackageFolder  # @UnusedImport


class CommonApplication(object):

    # static member
    _sourcePathsListDefault = ['src', '.']

    @staticmethod    
    def getSourcePathsListDefault():
        
        return CommonApplication._sourcePathsListDefault

    # static member
    _doNotEditMessage = 'Automatically-generated by XCDL. Do not edit!'

    @staticmethod    
    def getDoNotEditMessage():
        
        return CommonApplication._doNotEditMessage


    def __init__(self, *argv):
        
        self.argv = argv
        
        self.verbosity = 0

        # initialise the dictionary where all objects will be stored
        self.allObjectsDict = {}

        self.defaultScripts = ['meta/xcdl.py']
        
        self.indent = '   '

        return
    
    
    def processPackagesTrees(self, packagesFilePathList):
        
        # build a list of trees, for all given packages
        packagesTreesList = []
                
        for filePath in packagesFilePathList:
            
            packsList = self.processPackageTree(filePath)
            if packsList != None:
                packagesTreesList.extend(packsList)
        
        return packagesTreesList
    

    def processPackageTree(self, packagePath):
                        
        packageAbsolutePath = os.path.abspath(packagePath)

        if os.path.isdir(packageAbsolutePath):
            print 'Process package folder \'{0}\'.'.format(packagePath)
            rootList = self.processFolderRecursive(None, packageAbsolutePath)
        elif os.path.isfile(packagePath):
            print 'Process package file \'{0}\'.'.format(packagePath)
            # process the given script and recurse
            rootList = self.processScript(None, packageAbsolutePath)
        else:
            raise ErrorWithDescription("Path not a folder or a file")
        
        for node in rootList:
            node.setRepositoryFolderAbsolutePath(packageAbsolutePath)
                        
        return rootList


    def processConfigFile(self, configFilePath):
        
        print        
        print 'Process configuration file \'{0}\'.'.format(configFilePath)
        configFileAbsolutePath = os.path.abspath(self.configFilePath)
        
        # process the given script and recurse
        rootList = self.processScript(None, configFileAbsolutePath, None)
        return rootList
    
    
    def processFolderRecursive(self, parent, folderAbsolutePath):
        
        crtParent = parent
        localList = []
        for path in self.defaultScripts:
            tentativeFileAbsolutePath = os.path.join(folderAbsolutePath, path)
            if os.path.isfile(tentativeFileAbsolutePath):
                if self.verbosity > 2:
                    print 'is package'
                
                packageLocation = PackageLocation(folderAbsolutePath, tentativeFileAbsolutePath)
                localList = self.processScript(parent, tentativeFileAbsolutePath, packageLocation)
                crtParent = localList[0]
                break
                 
        for name in os.listdir(folderAbsolutePath):
            absolutePath = os.path.join(folderAbsolutePath, name)
            if os.path.isdir(absolutePath):
                if self.verbosity > 2:
                    print 'subfolder {0}'.format(absolutePath)
                self.processFolderRecursive(crtParent, absolutePath)
        
        return localList
    
    
    def processScript(self, parent, scriptAbsolutePath, packageLocation):
        
        if self.verbosity > 1:
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
            if len(node.getNonRecognisedKeywords()) > 0:
                print 'Ignored keywords {0} in {1}'.format(
                        node.getNonRecognisedKeywords(), node.getId())
        
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
                
                parentName = node.getParentId()
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
        parentName = node.getParentId()
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
        scriptsList = node.getIncludesList()
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
    
    
    def dumpTree(self, packagesTreesList, isLoaded):
        
        if not isLoaded:
            print "The packages trees:"
        else:
            print "The loaded packages trees:"
        
        print
        for tree in packagesTreesList:
            self.dumpTreeRecursive(tree, 0, isLoaded)
        return
    
        
    def dumpTreeRecursive(self, node, depth, isLoaded):
        
        if isLoaded and (not node.isLoaded()):
            return
        
        indent = '   '
        
        kind = ' ({0}'.format(node.getObjectType())
        if node.getCategory() != None:
            kind += ',{0}'.format(node.getCategory())
        kind += ')'
        
        kind += (' +E' if node.isEnabled() else ' -E')
        kind += (' +A' if node.isActive() else ' -A')
        
        print '{0}* {1} \'{2}\'{3}'.format(indent * depth, node.getId(),
                            node.getName(), kind)

        packageLocation = node.getPackageLocation()
        if packageLocation != None:
            print '{0}- packageFolder \'{1}\''.format(indent * (depth + 1),
                                    packageLocation.getFolderAbsolutePath())
            
        # dump sources, if any
        sourcesList = node.getSourceFilesList()
        if sourcesList != None:
            for source in sourcesList:
                print '{0}- sourceFile {1}'.format(indent * (depth + 1), source)

        # dump loadPackages, if any
        loadPackagesList = node.getLoadPackagesList()
        if loadPackagesList != None:
            for loadPackages in loadPackagesList:
                print '{0}- loadPackage {1}'.format(indent * (depth + 1), loadPackages)
                
        headerDefinition = node.getHeaderDefinition()
        if headerDefinition != None:
            print '{0}- headerDefinition {1}'.format(indent * (depth + 1), headerDefinition)
               
        headerPath = node.getHeaderFile()
        if headerPath != None:
            print '{0}- headerFile \'{1}\''.format(indent * (depth + 1), headerPath)
             
        children = node.getTreeChildrenList()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.dumpTreeRecursive(child, depth + 1, isLoaded)            
            
        return

    
    def dumpConfiguration(self, configTreesList):
        
        print "The configuration trees:"
        print
        for tree in configTreesList:
            self.dumpConfigurationRecursive(tree, 0)
        return
    
        
    def dumpConfigurationRecursive(self, node, depth):
        
        indent = self.indent
        kind = ' ({0})'.format(node.getObjectType())
            
        print '{0}* {1} \'{2}\'{3}'.format(indent * depth, node.getId(),
                            node.getName(), kind)

        # dump loadPackages, if any
        loadPackagesList = node.getLoadPackagesList()
        if loadPackagesList != None:
            for loadPackages in loadPackagesList:
                print '{0}- loadPackages {1}'.format(indent * (depth + 1), loadPackages)
        
        optionsList = node.getOptionsList()
        if optionsList != None and len(optionsList) > 0:
            for key in optionsList.keys():
                print'{0}- option {1}={2}'.format(indent * (depth + 1), key,
                                                  optionsList[key])
                     
        buildFolder = node.getBuildFolder()
        if buildFolder != None:
            print'{0}- buildFolder=\'{1}\''.format(indent * (depth + 1), buildFolder)

        preprocessorSymbols = node.getPreprocessorSymbolsList()
        if preprocessorSymbols != None:
            for preprocessorSymbol in preprocessorSymbols:
                print '{0}- preprocessorSymbol=\'{1}\''.format(indent * (depth + 1),
                                                            preprocessorSymbol)
                    
        children = node.getTreeChildrenList()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.dumpConfigurationRecursive(child, depth + 1)
                        
        return

    
    def loadConfiguration(self, configTreesList, sid):
        
        if self.verbosity > 1:
            print 'Load configuration id=\'{0}\''.format(sid)
            print
        
        if sid not in self.allObjectsDict:
            print 'Missing id, cancelled'
            return
        
        configNode = self.allObjectsDict[sid]
        print 'Load configuration node \'{0}\'.'.format(configNode.getName())
        
        updated = self.loadConfigNode(configNode, 0)
        print '{0} nodes loaded.'.format(updated)

        return configNode
    
    
    def loadConfigNode(self, configNode, depth):
        
        if configNode.getObjectType() != 'Configuration':
            raise ErrorWithDescription('Not a configuration node {0}'.format(configNode.getName()))
        
        indent = self.indent
        if self.verbosity > 1:
            print '{0}process {1}'.format(indent * depth, configNode.getId())

        updated = 0
        loadList = configNode.getLoadPackagesList()
        if loadList != None:
            for load in loadList:
                updated += self.loadPackageTreeNode(load, depth+1)
        
        treeParent = configNode.getTreeParent()
        if treeParent != None:
            if treeParent.getObjectType() != 'Configuration':
                updated += self.loadPackageTreeNode(treeParent.getId(), depth+1)
            else:
                updated += self.loadConfigNode(treeParent, depth+1)
               
        return updated
    
                
    def loadPackageTreeNode(self, treeNodeId, depth):

        if treeNodeId not in self.allObjectsDict:
            raise ErrorWithDescription('Missing node to load {0}'.format(treeNodeId))
        
        indent = self.indent

        treeNode = self.allObjectsDict[treeNodeId]
        if treeNode.getObjectType() == 'Configuration':
            updated = self.loadConfigNode(treeNode, depth+1)
            return updated
        
        treePackageNode = treeNode.getPackageTreeNode()
        if treePackageNode == None:
            updated = 0
            return updated
        
        if self.verbosity > 1:
            print '{0}load {1}'.format(indent * depth, treeNodeId)
            
        updated = treePackageNode.setIsLoadedRecursive()
        
        loadPackagesList = treePackageNode.getLoadPackagesList()
        if loadPackagesList != None:
            for loadPackages in loadPackagesList:
                updated += self.loadPackageTreeNode(loadPackages, depth+1)
                        
        return updated
    
    
    def dumpPreprocessorDefinitions(self, packagesTreesList):
        
        print "The preprocessor definitions:"
        
        print
        #for tree in packagesTreesList:
        #    self.dumpPreprocessorDefinitionsRecursive(tree, 0)
        
        headersDict = self.buildHeadersDict(packagesTreesList)
        for key in headersDict.iterkeys():
            headerLines = headersDict[key]
            print key
            for headerLine in headerLines:
                print headerLine
            
        return
    
    
    def dumpPreprocessorDefinitionsRecursive(self, node, depth):

        if not node.isLoaded():
            return
        
        headerLineAndFileName = node.getHeaderLineAndFileName()
        if headerLineAndFileName != None:
            
            (headerDefinition, headerFile) = headerLineAndFileName
            
            if self.verbosity:
                print 'process {0}'.format(node.getId())

            print 'file: \'{0}\''.format(headerFile)
            print headerDefinition
            print
             
        children = node.getTreeChildrenList()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.dumpPreprocessorDefinitionsRecursive(child, depth + 1)            


    def buildHeadersDict(self, packagesTreesList):
        
        headersDict = {}
        for tree in packagesTreesList:
            self.buildHeadersDictRecursive(tree, 0, headersDict)
            
        return headersDict

    
    def buildHeadersDictRecursive(self, node, depth, headersDict):

        if not node.isLoaded():
            return
        
        headerLineAndFileName = node.getHeaderLineAndFileName()
        if headerLineAndFileName != None:
            
            (headerDefinition, headerFile) = headerLineAndFileName
            
            if self.verbosity > 1:
                print 'process {0}'.format(node.getId())

                print 'file: \'{0}\''.format(headerFile)
                print headerDefinition
                print
             
            if headerFile not in headersDict:
                headersDict[headerFile] = []
                 
            headersDict[headerFile].append(headerDefinition)
            
        children = node.getTreeChildrenList()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.buildHeadersDictRecursive(child, depth + 1, headersDict)            
        
        return
    
    
    def dumpSourceFiles(self, packagesTreesList):
        
        print "The source files to compile:"
        
        print
        #for tree in packagesTreesList:
        #    self.dumpSourceFilesRecursive(tree, 0)
        
        sourcesDict = self.buildSourcesDict(packagesTreesList)
        for key in sourcesDict.iterkeys():
            sources = sourcesDict[key]
            print key
            for source in sources:
                print source
            
        return


    def dumpSourceFilesRecursive(self, node, depth):

        if not node.isLoaded():
            return
        
        if node.isActive():
            
            sourceFiles = node.getSourceFilesList()
            if sourceFiles != None:
            
                if self.verbosity:
                    print 'process {0}'.format(node.getId())

                packageFolder = node.getPackageLocation().getFolderAbsolutePath()
                #if self.verbosity:
                #    print 'package folder: \'{0}\''.format(packageFolder)

                treeRoot = node.getTreeRoot()
                buildSubFolder = treeRoot.getBuildSubFolderWithDefault()
                #if self.verbosity:
                #    print 'build subfolder: \'{0}\''.format(buildSubFolder)
                
                rootPackageFolder = treeRoot.getPackageLocation().getFolderAbsolutePath()
                #if self.verbosity:
                #    print 'root package folder: \'{0}\''.format(rootPackageFolder)
                
                sourcesPathsList = node.getSourcePathsListRecursive()
                if sourcesPathsList == None:
                    sourcesPathsList = CommonApplication.getSourcePathsListDefault()
                
                      
                for sourceFile in sourceFiles:
                    print 'source file: \'{0}\''.format(sourceFile)

                    foundSourcePath = None
                    for sourcePath in sourcesPathsList:
                        sourceAbsolutePath = os.path.join(packageFolder, sourcePath, sourceFile)
                        if os.path.isfile(sourceAbsolutePath):
                            print 'source file path: \'{0}\''.format(sourceAbsolutePath)
                            foundSourcePath = sourcePath
                            break
                        
                    if foundSourcePath == None:
                        print 'not found'
                        continue
                    
                    if not sourceAbsolutePath.startswith(rootPackageFolder):
                        print 'paths do not match'
                        continue
                    
                    subPath = sourceAbsolutePath[len(rootPackageFolder)+1:]
                    #print subPath
                    subPathList = subPath.split(os.sep)
                    #print subPathList
                    
                    buildPath = []
                    buildPath.append(buildSubFolder)
                    buildPath.extend(subPathList[:-1])
                    print 'build path: {0}'.format(os.sep.join(buildPath))
                    
                print
             
        children = node.getTreeChildrenList()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.dumpSourceFilesRecursive(child, depth + 1)            
    

    def buildSourcesDict(self, packagesTreesList):

        sourcesDict = {}
        for tree in packagesTreesList:
            self.buildSourcesDictRecursive(tree, 0, sourcesDict)
            
        return sourcesDict

    
    def buildSourcesDictRecursive(self, node, depth, sourcesDict):
        
        if not node.isLoaded():
            return
        
        if node.isActive():
            
            sourceFiles = node.getSourceFilesList()
            if sourceFiles != None:
            
                if self.verbosity > 1:
                    print 'process {0}'.format(node.getId())

                packageFolder = node.getPackageLocation().getFolderAbsolutePath()
                #if self.verbosity:
                #    print 'package folder: \'{0}\''.format(packageFolder)

                treeRoot = node.getTreeRoot()
                buildSubFolder = treeRoot.getBuildSubFolderWithDefault()
                #if self.verbosity:
                #    print 'build subfolder: \'{0}\''.format(buildSubFolder)
                
                rootPackageFolder = treeRoot.getPackageLocation().getFolderAbsolutePath()
                #if self.verbosity:
                #    print 'root package folder: \'{0}\''.format(rootPackageFolder)
                
                sourcesPathsList = node.getSourcePathsListRecursive()
                if sourcesPathsList == None:
                    sourcesPathsList = CommonApplication.getSourcePathsListDefault()
                
                      
                for sourceFile in sourceFiles:
                    if self.verbosity > 1:
                        print 'source file: \'{0}\''.format(sourceFile)

                    foundSourcePath = None
                    for sourcePath in sourcesPathsList:
                        sourceAbsolutePath = os.path.join(packageFolder, sourcePath, sourceFile)
                        if os.path.isfile(sourceAbsolutePath):
                            if self.verbosity > 1:
                                print 'source file path: \'{0}\''.format(sourceAbsolutePath)
                            foundSourcePath = sourcePath
                            break
                        
                    if foundSourcePath == None:
                        print 'not found'
                        continue
                    
                    if not sourceAbsolutePath.startswith(rootPackageFolder):
                        print 'paths do not match'
                        continue
                    
                    subPath = sourceAbsolutePath[len(rootPackageFolder)+1:]
                    #print subPath
                    subPathList = subPath.split(os.sep)
                    #print subPathList
                    
                    buildPathList = []
                    buildPathList.append(buildSubFolder)
                    buildPathList.extend(subPathList[:-1])
                    
                    buildPathString = os.sep.join(buildPathList)
                    if self.verbosity > 1:
                        print 'build path: {0}'.format(buildPathString)
                    
                    if buildPathString not in sourcesDict:
                        # add an empty list for this build path
                        sourcesDict[buildPathString] = []
                    
                    crtSourceDict = {}
                    crtSourceDict['fileName'] = sourceFile
                    #crtSourceDict['buildPathList'] = buildPathList
                    crtSourceDict['sourceAbsolutePath'] = sourceAbsolutePath
                    crtSourceDict['repoNode'] = node
                    
                    # append the current source file to the path
                    sourcesDict[buildPathString].append(crtSourceDict)
                if self.verbosity > 1:
                    print
             
        children = node.getTreeChildrenList()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.buildSourcesDictRecursive(child, depth + 1, sourcesDict)            
        