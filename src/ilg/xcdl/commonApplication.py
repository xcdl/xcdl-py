# -*- coding: utf-8 -*-

import os

from ilg.xcdl.errorWithDescription import ErrorWithDescription
from ilg.xcdl.object import Object

# WARNING: DO NOT REMOVE!
# the following are needed in executed scripts
from ilg.xcdl.component import Component #@UnusedImport
from ilg.xcdl.package import Package #@UnusedImport
from ilg.xcdl.configuration import Configuration #@UnusedImport


class CommonApplication(object):

    def __init__(self, *argv):
        
        self.argv = argv
        
        self.isVerbose = False

        # initialise the dictionary where all objects will be stored
        self.allObjectsDict = {}

        return
    
    
    def loadPackagesTrees(self, packagesFilePathList):
        
        # build a list of trees, for all given packages
        packagesTreesList = []
                
        for filePath in packagesFilePathList:
            
            packsList = self.loadPackageTree(filePath)
            packagesTreesList.extend(packsList)
        
        return packagesTreesList
    

    def loadPackageTree(self, filePath):
                
        absoluteFilePath = os.path.abspath(filePath)
        
        # process the given script and recurse
        rootList = self.processScript(None, absoluteFilePath)
        return rootList


    def loadConfig(self, configFilePath):
                
        absoluteConfigFilePath = os.path.abspath(self.configFilePath)
        
        # process the given script and recurse
        rootList = self.processScript(None, absoluteConfigFilePath)
        return rootList
    
    
    def processScript(self, parent, scriptAbsolutePath):
        
        #print 'processing {0}'.format(scriptAbsolutePath)
        #print 'from folder {0}'.format(folderAbsolutePath)
        
        # list used to collect all objects contributed by encountered 
        # constructors
        localList = []
        Object.setList(localList)
        
        if not os.path.isfile(scriptAbsolutePath):
            raise ErrorWithDescription('Missing script file \'{0}\''.
                                       format(scriptAbsolutePath))

        execfile(scriptAbsolutePath)
        
        self.warnNonParsedKeywords(localList)
        localList = self.linkChildrenNodes(localList)
        localList = self.linkNodesWithParent(localList)
        
        # process parsed nodes
        for obj in localList:            
            self.processNode(obj, parent, scriptAbsolutePath)
            
        # return the current list, useful for the root node,
        # all other use the parent to build the tree                    
        return localList


    def warnNonParsedKeywords(self, localList):

        for node in localList:            

            # warn if some of the keywords were not parsed
            if len(node.getNonParsedKeywords()) > 0:
                print 'Ignored keywords {0} in {1}'.format(
                        node.getNonParsedKeywords(), node.getName())
        
        return
        

    def linkChildrenNodes(self, localList):
                
        for node in localList:
            
            if node.getChildren() == None:
                continue
                
            #print 'has children {0}'.format(node.getName())
            for child in node.getChildren():
                #print 'child {0}'.format(child.getName())
                
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
                    if parentName == parentNode.getName():
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
    
    
    def processNode(self, node, parent, scriptAbsolutePath):
          
        # check if the name was already used
        if node.getName() in self.allObjectsDict:
                
            oldObject = self.allObjectsDict[node.getName()]
            oldKind = oldObject.getKind()
            oldDisplay = oldObject.getDisplay();
            raise ErrorWithDescription('Name {0} \'{1}\' redefined (was {2} \'{3}\''.
                            format(node.getName(), node.getDisplay(), oldKind, oldDisplay))
              
        # eventually process local parent
        parentName = node.getParentName()
        if parentName != None and parent != None:
            if parent.getName() != parentName:
                print 'Parent of {0} already is {1}, redefined as {2}, ignored'.format(
                                node.getName(), parent.getName(), parentName)
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

        # store current object in the global dictionary    
        self.allObjectsDict[node.getName()] = node
        
        # process inner scripts        
        scriptsList = node.getScripts()
        if scriptsList != None:
                
            baseRelativePath = node.getBasePath()
            (scriptAbsoluteFolder,_) = os.path.split(scriptAbsolutePath)
            baseAbsolutePath = os.path.abspath(os.path.join(
                                        scriptAbsoluteFolder, baseRelativePath))
                                
            for child in scriptsList:
                    
                # print child
                childAbsolutePath = os.path.abspath(os.path.join(
                                                baseAbsolutePath, child))
                # print childAbsolutePath
                    
                self.processScript(node, childAbsolutePath)
                
        
        # process children nodes recursively
        childrenList = node.getChildren()
        if childrenList != None:
            
            for child in childrenList:
                self.processNode(child, node, scriptAbsolutePath)
                
        return
    
    
    def dumpTree(self, packagesTreesList):
        
        print "The packages trees:"
        for tree in packagesTreesList:
            self.recurseDumpTree(tree, 0)
        return
    
        
    def recurseDumpTree(self, node, depth):
        
        indent = '  '
        
        kind = None
        if node.getKind() != None:
            kind = ' ({0}'.format(node.getKind())
            if node.getPlatform() != None:
                kind += ',{0}'.format(node.getPlatform())
            kind += ')'
            
        print '{0}{1} \'{2}\'{3}'.format(indent*depth, node.getName(), 
                            node.getDisplay(), kind)

        # dump sources, if any
        sourcesList = node.getCompile()
        if sourcesList != None and len(sourcesList) > 0:
            for source in sourcesList:
                print '{0}compile {1}'.format(indent*(depth+1), source)

        # dump sources, if any
        requiresList = node.getRequires()
        if requiresList != None and len(requiresList) > 0:
            for requires in requiresList:
                print '{0}requires {1}'.format(indent*(depth+1), requires)
                
        children = node.getTreeChildren()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.recurseDumpTree(child, depth+1)            
            
        return

    
    def dumpConfiguration(self, configTreesList):
        
        print "The configuration trees:"
        for tree in configTreesList:
            self.recurseDumpConfiguration(tree, 0)
        return
    
        
    def recurseDumpConfiguration(self, node, depth):
        
        indent = '  '
        
        kind = None
        if node.getKind() != None:
            kind = ' ({0})'.format(node.getKind())
            
        print '{0}{1} \'{2}\'{3}'.format(indent*depth, node.getName(), 
                            node.getDisplay(), kind)

        # dump sources, if any
        requiresList = node.getRequires()
        if requiresList != None and len(requiresList) > 0:
            for requires in requiresList:
                print '{0}requires {1}'.format(indent*(depth+1), requires)
        
        optionsList = node.getOptions()
        if optionsList != None and len(optionsList) > 0:
            for key in optionsList.keys():
                print'{0}option {1}={2}'.format(indent*(depth+1), key, optionsList[key])
                     
        buildFolder = node.getBuildFolder()
        if buildFolder != None:
            print'{0}buildFolder=\'{1}\''.format(indent*(depth+1), buildFolder)
            
        children = node.getTreeChildren()
        if children == None:
            return
        
        # iterate through all children
        for child in children:           
            self.recurseDumpConfiguration(child, depth+1)
                        
        return

    
    
