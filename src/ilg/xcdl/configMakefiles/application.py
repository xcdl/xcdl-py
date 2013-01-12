# -*- coding: utf-8 -*-

"""
Usage:
    python -m ilg.xcdl.configMakefiles [options]

Options:
        
    -c, --config
        the root configuration file
        
    -p, --packages
        the root of the packages tree file, multiple trees accepted
    
    -i, --id
        the ID of the configuration to be generated

    -o, --output
        the output folder
        
    -l, --linearise
        linearise the build subfolder
        
    -v, --verbose
        print progress output; more increase verbosity

    -h, --help
        print this message
        
Purpose:
    Create the build folders and the makefiles.
    
"""

import os
import getopt

from ilg.xcdl.commonApplication import CommonApplication
from ilg.xcdl.errorWithDescription import ErrorWithDescription


class Application(CommonApplication):
    
    def __init__(self, *argv):
                
        super(Application,self).__init__(*argv)

        # application specific members

        self.packagesFilePathList = []
        
        self.configFilePath = None
        
        self.desiredConfigurationId = None
        
        self.outputFolder = None
        
        self.doLinearise = False
        
        return
    

    def usage(self):
        
        print __doc__
        return


    def run(self):
        
        try:
            (opts, args) = getopt.getopt(self.argv[1:], 'c:p:i:o:lhv', 
                            ['config=', 'packages=', 'id=', 'output=', 
                             'linearise', 'help', 'verbose'])
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err) # will print something like "option -a not recognised"
            self.usage()
            return 2
        
        try:
            if len(args) > 0:
                print 'unused arguments: ', args
                self.usage()
                return 2
                    
            for (o, a) in opts:
                #a = a
                if o in ('-c', '--config'):
                    self.configFilePath = a
                elif o in ('-p', '--packages'):
                    self.packagesFilePathList.append(a)
                elif o in ('-i', '--id'):
                    self.desiredConfigurationId = a
                elif o in ('-o', '--output'):
                    self.outputFolder = a
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
            print err
    
        finally:
            if self.verbosity > 0:
                print   
                print '[done]'
            
        return 0        


    def validate(self):
        
        if len(self.packagesFilePathList) == 0:
            raise ErrorWithDescription('Missing --packages parameter')
        
        if self.configFilePath == None:
            raise ErrorWithDescription('Missing --config parameter')

        if self.desiredConfigurationId == None:
            raise ErrorWithDescription('Missing --id parameter')

        if self.outputFolder == None:
            raise ErrorWithDescription('Missing --output parameter')
                                
        return
    

    def process(self):
        
        if self.verbosity > 0:
            print
            print "* Create the build folders with distributed GNU Make files *"
            print
            if self.verbosity > 1:
                print 'Verbosity level {0}'.format(self.verbosity)
                print
        
        self.validate()
        
        packagesTreesList = self.processPackagesTrees(self.packagesFilePathList, 0)

        configTreesList = self.processConfigFile(self.configFilePath, 0)

        if self.verbosity > 1:
            print
            self.dumpTree(packagesTreesList, False)
        
            print
            self.dumpConfiguration(configTreesList)

        print
        configNode = self.loadConfiguration(configTreesList, 
                                            self.desiredConfigurationId, 0)

        if self.verbosity > 0:
            print
            print 'Process initial \'isEnabled\' properties...'
        self.processInitialIsEnabled(packagesTreesList)

        if self.verbosity > 0:
            print
            print 'Process \'requires\' properties...'
        self.processRequires(packagesTreesList)

        if self.verbosity > 1:
            print
            self.dumpTree(packagesTreesList, True)

        if not os.path.isdir(self.outputFolder):
            os.makedirs(self.outputFolder)
                                       
        outputSubFolder = configNode.getBuildFolderRecursiveWithSubstitutions()
        if self.doLinearise:
            outputSubFolder = outputSubFolder.replace(os.sep, '_')
        
        #print outputSubFolder
        
        if self.verbosity > 0:
            print
            print 'Generate header files...'
        self.generatePreprocessorDefinitions(packagesTreesList, self.outputFolder, outputSubFolder)
        
        if self.verbosity > 0:
            print
            print 'Generate Make files...'
        self.generateAllMakeFiles(packagesTreesList, configNode, self.outputFolder, outputSubFolder)
        
        return


    def generatePreprocessorDefinitions(self, packagesTreesList, outputFolder, outputSubFolder):
        
        headersDict = self.buildHeadersDict(packagesTreesList)
        for fileRelativePath in headersDict.iterkeys():
            
            fileAbsolutePath = os.path.join(outputFolder, outputSubFolder, fileRelativePath)
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


    def generateAllMakeFiles(self, packagesTreesList, configNode, outputFolder, outputSubFolder):
        
        sourcesDict = self.buildSourcesDict(packagesTreesList)
        for folderRelativePath in sourcesDict.iterkeys():
            
            folderAbsolutePath = os.path.join(outputFolder, outputSubFolder, folderRelativePath)
            if not os.path.isdir(folderAbsolutePath):
                if self.verbosity > 1:
                    print('Create folder \'{0}\''.format(folderAbsolutePath))
                os.makedirs(folderAbsolutePath)
            
            self.generateSubdirMk(folderAbsolutePath, sourcesDict, folderRelativePath, outputFolder, outputSubFolder)
        
        artifactFileName = configNode.getArtifactFileNameRecursive()
        if artifactFileName == None:
            raise ErrorWithDescription('Missing artifact file name in configuration')
        
        self.generateRootMakeFiles(sourcesDict, outputFolder, outputSubFolder, artifactFileName)
            
        return

    
    def generateSubdirMk(self, folderAbsolutePath, sourcesDict, folderRelativePath, outputFolder, outputSubFolder):
        
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
        
        ccList = self.groupSourceFilesByType(sources, ['.c'])
        cppList = self.groupSourceFilesByType(sources, ['.cpp'])
        asmList = self.groupSourceFilesByType(sources, ['.S'])
                
        if len(ccList) > 0:
            f.write('C_SRCS += \\\n')
            
            for e in ccList:
                p = e['sourceAbsolutePath']
                f.write(self.expandPathSpaces(p))
                f.write(' \\\n')
            f.write('\n')
        
        if len(cppList) > 0:
            f.write('CPP_SRCS += \\\n')
            
            for e in cppList:
                p = e['sourceAbsolutePath']
                f.write(self.expandPathSpaces(p))
                f.write(' \\\n')
            f.write('\n')

        # TODO: process assembly files

        allList = []
        allList.extend(ccList)
        allList.extend(cppList)
        allList.extend(asmList)
         
        if len(allList) > 0:
            f.write('{0} += \\\n'.format('BCS'))
            
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
                    toolName = 'clang++'
                    toolDesc = 'LLVM Clang++'
                elif fType == '.c':
                    toolName = 'clang'
                    toolName = 'LLVM Clang'
                
                if self.verbosity > 0:
                    print '- compile \'{0}\' with \'{1}\''.format(sourceAbsolutePath, toolDesc)

                f.write('\t@echo \'Invoking: {0}\'\n'.format(toolDesc))
                
                f.write('\t{0}'.format(toolName))
                f.write(' -DDEBUG=1')
                
                buildFolderAbsolutePath=os.path.abspath(os.path.join(outputFolder, outputSubFolder))
                includeAbsolutePathList = self.computeIncludeAbsolutePathList(e['repoNode'], fileNameComplete, buildFolderAbsolutePath)
                for includeAbsolutePath in includeAbsolutePathList:
                    f.write(' -I"{0}"'.format(includeAbsolutePath))
                    
                f.write(' -O0 -emit-llvm -g3 -Wall -c -fmessage-length=0 -fsigned-char')
                f.write(' -MMD -MP -o "$@" "$<"')
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
        

    def generateRootMakeFiles(self, sourcesDict, outputFolder, outputSubFolder, artifactFileName):
        
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
        f.write('ifneq ($(strip $(CC_DEPS)),)\n')
        f.write('-include $(CC_DEPS)\n')
        f.write('endif\n')
        f.write('ifneq ($(strip $(CPP_DEPS)),)\n')
        f.write('-include $(CPP_DEPS)\n')
        f.write('endif\n')
        # TODO: add assembly files
        f.write('endif\n')
        f.write('\n')
        
        f.write('-include ../makefile.defs\n')
        f.write('\n')

        f.write('# Add inputs and outputs from these tool invocations to the build variables\n')
        f.write('\n')

        toolDesc = 'LLVM C++ linker'
        
        f.write('# Tool invocations\n')
        f.write('{0}: $(BCS) $(USER_OBJS)\n'.format(artifactFileName))
        f.write('\t@echo \'Linking XCDL target: $@\'\n')
        f.write('\t@echo \'Invoking: {0}\'\n'.format(toolDesc))
        f.write('\t{0} -native -o "{1}" $(BCS) $(USER_OBJS) $(LIBS)\n'.format('clang++', artifactFileName))
        f.write('\t@echo \'Finished linking target: $@\'\n')
        f.write('\t@echo \' \'\n')
        f.write('\n')

        if self.verbosity > 0:
            print '- link \'{0}\' with \'{1}\''.format(artifactFileName, toolDesc)

        f.write('# Other Targets\n')
        f.write('clean:\n')
        f.write('\t-$(RM) $(BCS)$(CC_DEPS)$(CPP_DEPS)$(LLVM_BC_EXECUTABLES) {0}\n'.format(artifactFileName))
        f.write('\t@echo \' \'\n')
        f.write('\n')
        
        f.write('secondary-outputs: $(LLVM_BC_EXECUTABLES)\n')
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
        f.write('CC_SRCS :=\n')
        f.write('CPP_DEPS :=\n')
        f.write('CC_DEPS :=\n')
        f.write('LLVM_BC_EXECUTABLES :=\n')
        f.write('\n')

        f.write('# Every subdirectory with source files must be described here\n')
        f.write('SUBDIRS := \\\n')

        for folder in sourcesDict.iterkeys():
            f.write('{0} \\\n'.format(self.expandPathSpaces(folder)))        
        f.write('\n')

        f.close()
        
        
        return
    
    