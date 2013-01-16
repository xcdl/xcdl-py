# -*- coding: utf-8 -*-

"""
Usage:
    sh configMakefiles.sh [params]
    python -m ilg.xcdl.configMakefiles [params]

Params:
        
    -c, --config
        the relative/absolute path to the configuration file. (mandatory)
        
    -r, --repository
        the relative/absolute path to the repository folder;
        multiple repositories accepted.
    
    -i, --id
        the ID of the configuration to be generated; can be a leaf node 
        or a subtree to create multiple configurations from a single run.
        (mandatory)

    -b, --build
        the output folder, where the build configurations will be created.
        (mandatory)
        
    -t, --toolchain
        the ID of the toolchain to be used;
        overwrite the toolchain refered in the configuration with this one.
        
    -l, --linearise
        linearise the build subfolder to shorten the path.
        
    -v, --verbose
        print progress output; more occurences increase verbosity.

    -h, --help
        print this message.
        
Purpose:
    Create the build folders with distributed GNU Make files.
    
"""

import os
import getopt

from ilg.xcdl.commonApplication import CommonApplication
from ilg.xcdl.errorWithDescription import ErrorWithDescription


class Application(CommonApplication):
    
    def __init__(self, *argv):
                
        super(Application,self).__init__(*argv)

        # application specific members

        self.packagesAbsolutePathList = []
        
        self.configFilePath = None
        
        self.desiredConfigurationId = None
        
        self.outputFolder = None
        
        self.doLinearise = False
        
        self.toolchainId = None
        
        return
    

    def usage(self):
        
        print __doc__
        return


    def run(self):
        
        try:
            (opts, args) = getopt.getopt(self.argv[1:], 'c:r:i:b:t:lhv', 
                            ['config=', 'repository=', 'id=', 'build=', 
                             'toolchain=', 'linearise', 'help', 'verbose'])
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err) # will print something like "option -a not recognised"
            self.usage()
            return 2
        
        retval = 0
        try:
            if len(args) > 0:
                print 'Unused arguments: '
                for arg in args:
                    print '\t{0}'.format(arg)
                self.usage()
                return 2
                    
            for (o, a) in opts:
                #a = a
                if o in ('-c', '--config'):
                    self.configFilePath = a
                elif o in ('-r', '--repository'):
                    self.packagesAbsolutePathList.append(a)
                elif o in ('-i', '--id'):
                    self.desiredConfigurationId = a
                elif o in ('-b', '--build'):
                    self.outputFolder = a
                elif o in ('-t', '--toolchain'):
                    self.toolchainId = a
                elif o in ('-l', '--linearise'):
                    self.doLinearise = True
                elif o in ('-v', '--verbose'):
                    self.verbosity += 1
                elif o in ('-h', '--help'):
                    self.usage()
                    return 0
                else:
                    assert False, 'option not handled'

            CommonApplication.setVerbosity(self.verbosity)
            self.process()
            
        except ErrorWithDescription as err:
            print 'ERROR: {0}'.format(err)
            retval = 1
    
        finally:
            if self.verbosity > 0:
                print   
                print '[done]'
            
        return retval        


    def validate(self):
        
        if self.configFilePath == None:
            raise ErrorWithDescription('Missing mandatory --config= parameter')

        if self.desiredConfigurationId == None:
            raise ErrorWithDescription('Missing mandatory --id= parameter')

        if self.outputFolder == None:
            raise ErrorWithDescription('Missing mandatory --build= parameter')
                                
        return


    def validateToolchain(self, configNode):
        
        toolchainId = None
        toolchainNode = None
        
        if self.toolchainId != None:
            toolchainId = self.toolchainId
            if CommonApplication.isObjectById(toolchainId):
                toolchainNode = CommonApplication.getObjectById(toolchainId)
            else:
                print 'ERROR: param toolchain \'{0}\' not found, ignored'.format(toolchainId)
                toolchainId = None

        if toolchainId == None:           
            toolchainId = configNode.getToolchainId()
            
            if toolchainId != None and CommonApplication.isObjectById(toolchainId):
                toolchainNode = CommonApplication.getObjectById(toolchainId)
            else:
                print 'ERROR: config toolchain \'{0}\' not found, ignored'.format(toolchainId)
                toolchainId = None
            
        if toolchainNode == None:
            raise ErrorWithDescription('Mandatory toolchain definition missing, quitting')

        return (toolchainNode, toolchainId)

    def process(self):
        
        if self.verbosity > 0:
            print
            print '* The configMakefiles tool (part of the XCDL framework)    *'
            print '* Create the build folders with distributed GNU Make files *'
            print
            if self.verbosity > 1:
                print 'Verbosity level {0}'.format(self.verbosity)
                print
        
        self.validate()
        
        (configTreesList,repoFolderAbsolutePathList) = self.parseConfigurationFile(self.configFilePath, 0)

        self.packagesAbsolutePathList.extend(repoFolderAbsolutePathList)
        
        
        if self.verbosity > 1:
            print
            self.dumpConfiguration(configTreesList)

        if self.verbosity > 0:
            print
        repositoriesList = self.parseRepositories(self.packagesAbsolutePathList, 0)

        if self.verbosity > 1:
            print
            self.dumpTree(repositoriesList, False)
        
        if self.verbosity > 0:
            print
        configNode = self.loadConfiguration(configTreesList, 
                                            self.desiredConfigurationId, 0)

        if self.verbosity > 0:
            print
            print 'Build preprocessor symbols dictionary...'
        count = self.processSymbolsDict(repositoriesList)
        if self.verbosity > 0:
            print '- {0} symbol(s) processed.'.format(count)
        
        if self.verbosity > 0:
            print
            print 'Evaluate the initial \'isEnabled\' expressions, if any...'
        self.processInitialIsEnabled(repositoriesList)

        if self.verbosity > 0:
            print
            print 'Process the \'requires\' properties...'
        self.processRequiresProperties(repositoriesList, configNode, False)

        # and one more time, to report remaining errors
        CommonApplication.clearErrorCount()
        self.processRequiresProperties(repositoriesList, configNode, True)
        count = CommonApplication.getErrorCount()
        if count == 1:
            raise ErrorWithDescription('1 requirement not satisfied, quitting')
        elif count > 1:
            raise ErrorWithDescription('{0} requirements not satisfied, quitting'.format(count))

        if self.verbosity > 1:
            print
            self.dumpTree(repositoriesList, True)

        if not os.path.isdir(self.outputFolder):
            os.makedirs(self.outputFolder)
                                       
        outputSubFolder = configNode.getBuildFolderRecursiveWithSubstitutions()
        if self.doLinearise:
            outputSubFolder = outputSubFolder.replace(os.sep, '_')
        
        #print outputSubFolder

        if self.verbosity > 0:
            print
            print 'Generate header files...'
        self.generatePreprocessorDefinitions(repositoriesList, self.outputFolder, outputSubFolder)
        
        (toolchainNode,_) = self.validateToolchain(configNode)
        if self.verbosity > 0:
            print
            print 'Using toolchain \'{0}\'.'.format(toolchainNode.getName())
            
        if self.verbosity > 0:
            print
            print 'Generate GNU Make files...'
        self.generateAllMakeFiles(repositoriesList, configNode, toolchainNode, self.outputFolder, outputSubFolder)
        
        return


    def generatePreprocessorDefinitions(self, repositoriesList, outputFolder, outputSubFolder):
        
        headersDict = self.buildHeadersDict(repositoriesList)
        for fileRelativePath in headersDict.iterkeys():
            
            fileAbsolutePath = os.path.abspath(os.path.join(outputFolder, outputSubFolder, fileRelativePath))
            if self.verbosity > 1:
                print fileAbsolutePath

            (folderAbsolutePath,_) = os.path.split(fileAbsolutePath)
            if not os.path.isdir(folderAbsolutePath):
                if self.verbosity > 1:
                    print('Create folder \'{0}\''.format(folderAbsolutePath))
                os.makedirs(folderAbsolutePath)
            
            if self.verbosity > 0:
                if not os.path.isfile(fileAbsolutePath):
                    print('Write file \'{0}\''.format(fileAbsolutePath))
                else:
                    print('Overwrite file \'{0}\''.format(fileAbsolutePath))

            # truncate existing files
            textFile = open(fileAbsolutePath, 'w')
            
            doNotEditMessage = CommonApplication.getDoNotEditMessage()
            
            textFile.write('//{0}//\n'.format('/'*(len(doNotEditMessage)+2)))
            textFile.write('// {0} //\n'.format(doNotEditMessage))
            textFile.write('//{0}//\n'.format('/'*(len(doNotEditMessage)+2)))
            textFile.write('\n')
            
            headerLines = headersDict[fileRelativePath]
            for headerLine in headerLines:
                if self.verbosity > 0:
                    print '- {0}'.format(headerLine)
                textFile.write(headerLine)
                textFile.write('\n')
                
            textFile.close()

        if self.verbosity > 1:
            print
            
        return


    def generateAllMakeFiles(self, repositoriesList, configNode, toolchainNode, outputFolder, outputSubFolder):
        
        # build a dictionary of sources, grouped by folder relative path
        sourcesDict = self.buildSourcesDict(repositoriesList)
        
        # iterate all folders
        for folderRelativePath in sourcesDict.iterkeys():
            
            folderAbsolutePath = os.path.abspath(os.path.join(outputFolder, outputSubFolder, folderRelativePath))
            if not os.path.isdir(folderAbsolutePath):
                if self.verbosity > 1:
                    print('Create folder \'{0}\''.format(folderAbsolutePath))
                os.makedirs(folderAbsolutePath)
            
            self.generateSubdirMk(sourcesDict, folderAbsolutePath, folderRelativePath, configNode, toolchainNode, outputFolder, outputSubFolder)
        
        artifactFileName = configNode.getArtifactFileNameRecursive()
        if artifactFileName == None:
            raise ErrorWithDescription('Missing artifact file name in configuration')
        
        self.generateRootMakeFiles(sourcesDict, toolchainNode, artifactFileName, outputFolder, outputSubFolder)
            
        return

    
    def generateSubdirMk(self, sourcesDict, folderAbsolutePath, folderRelativePath, configNode, toolchainNode, outputFolder, outputSubFolder):
        
        subdirAbsolutePath = os.path.join(folderAbsolutePath, 'subdir.mk')
        
        if self.verbosity > 0:
            if not os.path.isfile(subdirAbsolutePath):
                print('Write file \'{0}\''.format(subdirAbsolutePath))
            else:
                print('Overwrite file \'{0}\''.format(subdirAbsolutePath))

        f = open(subdirAbsolutePath, 'w')
        
        self.generateDoNotEditMessage(f)
        f.write('# Add inputs and outputs from these tool invocations to the build variables\n')
        
        sources = sourcesDict[folderRelativePath]
        
        cppList = self.groupSourceFilesByType(sources, ['.cpp'])
        cList = self.groupSourceFilesByType(sources, ['.c'])
        sList = self.groupSourceFilesByType(sources, ['.S'])
                
        if len(cppList) > 0:
            f.write('CPP_SRCS += \\\n')
            
            for e in cppList:
                p = e['sourceAbsolutePath']
                f.write(self.expandPathSpaces(p))
                f.write(' \\\n')
            f.write('\n')

        if len(cList) > 0:
            f.write('C_SRCS += \\\n')
            
            for e in cList:
                p = e['sourceAbsolutePath']
                f.write(self.expandPathSpaces(p))
                f.write(' \\\n')
            f.write('\n')
        
        if len(sList) > 0:
            f.write('S_SRCS += \\\n')
            
            for e in sList:
                p = e['sourceAbsolutePath']
                f.write(self.expandPathSpaces(p))
                f.write(' \\\n')
            f.write('\n')
        

        allList = []
        allList.extend(cppList)
        allList.extend(cList)
        allList.extend(sList)
        
        makeObjectsVariable = toolchainNode.getPropertyRecursive('makeObjectsVariable')
        if makeObjectsVariable == None:
            makeObjectsVariable = 'OBJS'    # default make variable name
 
        if len(allList) > 0:
            f.write('{0} += \\\n'.format(makeObjectsVariable))
            
            for e in allList:
                fileNameComplete = e['fileName']
                (fileName, _) = os.path.splitext(fileNameComplete)
                p = os.path.join('.', folderRelativePath, '{0}.{1}'.format(fileName, 'bc'))
                f.write(self.expandPathSpaces(p))
                f.write(' \\\n')
            f.write('\n')

        if len(cppList) > 0:
            f.write('CPP_DEPS += \\\n')
            
            for e in cppList:
                fileNameComplete = e['fileName']
                (fileName, _) = os.path.splitext(fileNameComplete)
                p = os.path.join('.', folderRelativePath, '{0}.{1}'.format(fileName, 'd'))
                f.write(self.expandPathSpaces(p))
                f.write(' \\\n')
            f.write('\n')

        if len(cList) > 0:
            f.write('C_DEPS += \\\n')
            
            for e in cList:
                fileNameComplete = e['fileName']
                (fileName, _) = os.path.splitext(fileNameComplete)
                p = os.path.join('.', folderRelativePath, '{0}.{1}'.format(fileName, 'd'))
                f.write(self.expandPathSpaces(p))
                f.write(' \\\n')
            f.write('\n')

        if len(sList) > 0:
            f.write('S_DEPS += \\\n')
            
            for e in sList:
                fileNameComplete = e['fileName']
                (fileName, _) = os.path.splitext(fileNameComplete)
                p = os.path.join('.', folderRelativePath, '{0}.{1}'.format(fileName, 'd'))
                f.write(self.expandPathSpaces(p))
                f.write(' \\\n')
            f.write('\n')

        if len(allList) > 0:
            f.write('# Each subdirectory must supply rules for building sources it contributes\n')
               
            for e in allList:
                fileNameComplete = e['fileName']
                (fileName, _) = os.path.splitext(fileNameComplete)
                p = os.path.join(folderRelativePath, '{0}.{1}'.format(fileName, 'bc'))
                sourceAbsolutePath = e['sourceAbsolutePath']
                f.write('{0}: {1}\n'.format(self.expandPathSpaces(p), self.expandPathSpaces(sourceAbsolutePath)))
                f.write('\t@echo \'Compiling XCDL file: $<\'\n')
                                   
                fType = e['type']
                if fType == '.cpp':
                    tool = toolchainNode.getToolRecursive('cpp')
                    if tool == None:
                        print 'WARN: Missing \'cpp\' tool in toolchain \'{0}\', using defaults'.format(toolchainNode.getName())                      
                        toolName = 'g++'
                        toolDesc = 'GNU default g++'
                    else:
                        toolName = tool.getProgramName()
                        if toolName == None:
                            print 'WARN: Missing \'programName\' in tool \'cpp\', toolchain \'{0}\', using default \'g++\''.format(toolchainNode.getName())                      
                            toolName = 'g++'
                        toolDesc = tool.getDescription()
                        if toolDesc == None:
                            print 'WARN: Missing \'description\' in tool \'cpp\', toolchain \'{0}\', using default\'GNU default g++\''.format(toolchainNode.getName())                      
                            toolDesc = 'GNU default g++'
                        
                elif fType == '.c':
                    tool = toolchainNode.getToolRecursive('cc')
                    if tool == None:                        
                        print 'WARN: Missing \'cc\' tool in toolchain \'{0}\', using defaults'.format(toolchainNode.getName())                      
                        toolName = 'gcc'
                        toolDesc = 'GNU default gcc'
                    else:
                        toolName = tool.getProgramName()
                        if toolName == None:
                            print 'WARN: Missing \'programName\' in tool \'cc\', toolchain \'{0}\', using default \'gcc\''.format(toolchainNode.getName())                      
                            toolName = 'gcc'
                        toolDesc = tool.getDescription()
                        if toolDesc == None:
                            print 'WARN: Missing \'description\' in tool \'cc\', toolchain \'{0}\', using default \'GNU default gcc\''.format(toolchainNode.getName())                      
                            toolDesc = 'GNU default gcc'
                
                elif fType == '.S':
                    tool = toolchainNode.getToolRecursive('asm')
                    if tool == None:                        
                        print 'WARN: Missing \'asm\' tool in toolchain \'{0}\', using defaults'.format(toolchainNode.getName())                      
                        toolName = 'gcc'
                        toolDesc = 'GNU default gcc'
                    else:
                        toolName = tool.getProgramName()
                        if toolName == None:
                            print 'WARN: Missing \'programName\' in tool \'asm\', toolchain \'{0}\', using default \'gcc\''.format(toolchainNode.getName())                      
                            toolName = 'gcc'
                        toolDesc = tool.getDescription()
                        if toolDesc == None:
                            print 'WARN: Missing \'description\' in tool \'asm\', toolchain \'{0}\', using default \'GNU default gcc\''.format(toolchainNode.getName())                      
                            toolDesc = 'GNU default gcc'
                
                if self.verbosity > 0:
                    #print '- compile \'{0}\' with \'{1}\''.format(sourceAbsolutePath, toolDesc)
                    eList = e['buildPathList']
                    ePath = os.path.join(os.sep.join(eList[1:]), fileNameComplete)
                    print '- compile {0} \'{1}\''.format(eList[0], ePath)

                f.write('\t@echo \'Invoking: {0}\'\n'.format(toolDesc))
                
                f.write('\t{0}'.format(toolName))
                
                preprocessorSymbolsList = configNode.getPreprocessorSymbolsList()
                if preprocessorSymbolsList != None:
                    for preprocessorSymbol in preprocessorSymbolsList:
                        f.write(' -D{0}'.format(preprocessorSymbol))
                
                buildFolderAbsolutePath=os.path.abspath(os.path.join(outputFolder, outputSubFolder))
                includeAbsolutePathList = self.computeIncludeAbsolutePathList(e['repoNode'], fileNameComplete, buildFolderAbsolutePath)
                for includeAbsolutePath in includeAbsolutePathList:
                    f.write(' -I"{0}"'.format(includeAbsolutePath))
                
                compilerOptimisationOptions = toolchainNode.getPropertyRecursive('compilerOptimisationOptions')
                if compilerOptimisationOptions == None:
                    compilerOptimisationOptions = '-O'
                f.write(' {0}'.format(compilerOptimisationOptions))
                
                compilerDebugOptions = toolchainNode.getPropertyRecursive('compilerDebugOptions')
                if compilerDebugOptions == None:
                    compilerDebugOptions = '-g'
                f.write(' {0}'.format(compilerDebugOptions))
                    
                compilerWarningOptions = toolchainNode.getPropertyRecursive('compilerWarningOptions')
                if compilerWarningOptions == None:
                    compilerWarningOptions = '-Wall'
                f.write(' {0}'.format(compilerWarningOptions))

                compilerMiscOptions = toolchainNode.getPropertyRecursive('compilerMiscOptions')
                if compilerMiscOptions == None:
                    compilerMiscOptions = '-fmessage-length=0 -c'
                f.write(' {0}'.format(compilerMiscOptions))
                    
                compilerDepsOptions = toolchainNode.getPropertyRecursive('compilerDepsOptions')
                if compilerDepsOptions == None:
                    compilerDepsOptions = '-MMD -MP'
                f.write(' {0}'.format(compilerDepsOptions))
                    
                compilerOutputOptions = toolchainNode.getPropertyRecursive('compilerOutputOptions')
                if compilerOutputOptions == None:
                    compilerOutputOptions = '-o "$@"'
                f.write(' {0}'.format(compilerOutputOptions))

                compilerInputOptions = toolchainNode.getPropertyRecursive('compilerInputOptions')
                if compilerInputOptions == None:
                    compilerInputOptions = '"$<"'
                f.write(' {0}'.format(compilerInputOptions))

                f.write('\n')
                
                f.write('\t@echo \'Finished compiling file: $<\'\n')
                f.write('\t@echo \' \'\n')
                f.write('\n')
                                
        f.close()

        return
   
   
    def computeIncludeAbsolutePathList(self, treeNode, fileNameComplete, buildFolderAbsolutePath):
        
        localList = []
        if treeNode == None:
            print 'Internal error: Missing node for source {0}'.format(fileNameComplete)
        else:
            packageTreeNode = treeNode.getPackageTreeNode()
            if packageTreeNode == None:
                print 'Internal error: Missing parent node for source {0}'.format(fileNameComplete)
            else:
                localList2 = packageTreeNode.getBuildIncludeFoldersRecursive()
                
                for path in localList2:
                    if path.find('$(REPO_DIR)') != -1:
                        repoFolder = treeNode.getTreeRoot().getRepositoryFolderAbsolutePath()
                        path = path.replace('$(REPO_DIR)', repoFolder)
                    elif path.find('$(BUILD_DIR)') != -1:
                        path = path.replace('$(BUILD_DIR)', buildFolderAbsolutePath)

                    # add replaced or original path o response list
                    localList.append(path)
                                       
        return localList
        

    def generateDoNotEditMessage(self, builtinFile):
        
        doNotEditMessagee = CommonApplication.getDoNotEditMessage()
        builtinFile.write('#{0}#\n'.format('#'*(len(doNotEditMessagee)+2)))
        builtinFile.write('# {0} #\n'.format(doNotEditMessagee))
        builtinFile.write('#{0}#\n'.format('#'*(len(doNotEditMessagee)+2)))
        builtinFile.write('\n')
        
        return
    
    
    def groupSourceFilesByType(self, sources, extList):
        
        resultList = []
        for source in sources:
            fileName = source['fileName']
            (_,fileExt) = os.path.splitext(fileName)

            if fileExt in extList:
                resultList.append(source)
                
                # store current type in dictionary
                if 'type' not in source:
                    source['type'] = extList[0]
                    
        return resultList
    
  
    def expandPathSpaces(self, path):
        
        return path.replace(' ', '\\ ')
        

    def generateRootMakeFiles(self, sourcesDict, toolchainNode, artifactFileName, outputFolder, outputSubFolder):
        
        makefileAbsolutePath = os.path.join(outputFolder, outputSubFolder, 'makefile')
        
        if self.verbosity > 0:
            if not os.path.isfile(makefileAbsolutePath):
                print('Write file \'{0}\''.format(makefileAbsolutePath))
            else:
                print('Overwrite file \'{0}\''.format(makefileAbsolutePath))

        f = open(makefileAbsolutePath, 'w')
        
        self.generateDoNotEditMessage(f)

        f.write('\n')
        f.write('-include ../makefile.init\n')        
        f.write('\n')
        f.write('-RM := {0} -rf\n'.format('rm'))        
        f.write('\n')

        f.write('# All Target\n')
        f.write('all: {0} secondary-outputs\n'.format(artifactFileName))
        f.write('\n')

        f.write('# All of the sources participating in the build are defined here\n')        
        f.write('-include sources.mk\n')
        
        for folder in sourcesDict.iterkeys():
            subdirMkRelativePath = os.path.join(folder, 'subdir.mk')
            f.write('-include {0}\n'.format(self.expandPathSpaces(subdirMkRelativePath)))        

        f.write('-include objects.mk\n')
        f.write('\n')

        f.write('ifneq ($(MAKECMDGOALS),clean)\n')
        f.write('ifneq ($(strip $(CPP_DEPS)),)\n')
        f.write('-include $(CPP_DEPS)\n')
        f.write('endif\n')
        f.write('ifneq ($(strip $(C_DEPS)),)\n')
        f.write('-include $(C_DEPS)\n')
        f.write('endif\n')
        f.write('ifneq ($(strip $(S_DEPS)),)\n')
        f.write('-include $(S_DEPS)\n')
        f.write('endif\n')
        f.write('endif\n')
        f.write('\n')
        
        f.write('-include ../makefile.defs\n')
        f.write('\n')

        f.write('# Add inputs and outputs from these tool invocations to the build variables\n')
        f.write('\n')

        tool = toolchainNode.getToolRecursive('ld')
        if tool == None:
            print 'No linker define for toolchain \'\', using defaults'.format(toolchainNode.getName())
            
            toolDesc = 'Default g++'
            toolPgmName = 'g++'
        else:           
            toolDesc = tool.getDescription()
            toolPgmName = tool.getProgramName()
        
        makeObjectsVariable = toolchainNode.getPropertyRecursive('makeObjectsVariable')
        if makeObjectsVariable == None:
            makeObjectsVariable = 'OBJS'    # default make variable name
            
        linkerMiscOptions = toolchainNode.getPropertyRecursive('linkerMiscOptions')
        if linkerMiscOptions == None:
            linkerMiscOptions = ''          # empty default misc options
            
        toolOptions = tool.getOptions()
        if toolOptions == None:
            toolOptions = ''                # empty default tool options
            
        f.write('# Tool invocations\n')
        f.write('{0}: $({1}) $(USER_OBJS)\n'.format(artifactFileName, makeObjectsVariable))
        f.write('\t@echo \'Linking XCDL target: $@\'\n')
        f.write('\t@echo \'Invoking: {0}\'\n'.format(toolDesc))
        f.write('\t{0} {1} {2} -o "{3}" $({4}) $(USER_OBJS) $(LIBS)\n'.format(
                            toolPgmName, linkerMiscOptions, toolOptions,
                            artifactFileName, makeObjectsVariable))
        f.write('\t@echo \'Finished linking target: $@\'\n')
        f.write('\t@echo \' \'\n')
        f.write('\n')

        if self.verbosity > 0:
            print '- link \'{0}\' with \'{1}\''.format(artifactFileName, toolDesc)

        f.write('# Other Targets\n')
        f.write('clean:\n')
        f.write('\t-$(RM) $({0}) $(CPP_DEPS) $(C_DEPS) $(S_DEPS) $(CUSTOM_EXECUTABLES) {1}\n'.format(makeObjectsVariable, artifactFileName))
        f.write('\t@echo \' \'\n')
        f.write('\n')
        
        f.write('secondary-outputs: $(CUSTOM_EXECUTABLES)\n')
        f.write('\n')

        f.write('.PHONY: all clean dependents\n')
        f.write('.SECONDARY:\n')
        f.write('\n')

        f.write('-include ../makefile.targets\n')
        f.write('\n')
        
        f.close()

        # ---------------------------------------------------------------------
        
        objectsMkAbsolutePath = os.path.join(outputFolder, outputSubFolder, 'objects.mk')
        
        if self.verbosity > 0:
            if not os.path.isfile(objectsMkAbsolutePath):
                print('Write file \'{0}\''.format(objectsMkAbsolutePath))
            else:
                print('Overwrite file \'{0}\''.format(objectsMkAbsolutePath))

        f = open(objectsMkAbsolutePath, 'w')
        
        self.generateDoNotEditMessage(f)

        f.write('USER_OBJS :=\n')
        f.write('\n')

        f.write('LIBS :=\n')
        f.write('\n')

        f.close()
        
        # ---------------------------------------------------------------------
        
        sourcesMkAbsolutePath = os.path.join(outputFolder, outputSubFolder, 'sources.mk')
        
        if self.verbosity > 0:
            if not os.path.isfile(sourcesMkAbsolutePath):
                print('Write file \'{0}\''.format(sourcesMkAbsolutePath))
            else:
                print('Overwrite file \'{0}\''.format(sourcesMkAbsolutePath))

        f = open(sourcesMkAbsolutePath, 'w')
        
        self.generateDoNotEditMessage(f)

        f.write('CPP_SRCS :=\n')
        f.write('C_SRCS :=\n')
        f.write('S_SRCS :=\n')
        f.write('CPP_DEPS :=\n')
        f.write('C_DEPS :=\n')
        f.write('S_DEPS :=\n')
        f.write('CUSTOM_EXECUTABLES :=\n')
        f.write('\n')

        f.write('# Every subdirectory with source files must be described here\n')
        f.write('SUBDIRS := \\\n')

        for folder in sourcesDict.iterkeys():
            f.write('{0} \\\n'.format(self.expandPathSpaces(folder)))        
        f.write('\n')

        f.close()
        
        
        return
    
    