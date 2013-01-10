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
        
    -v, --verbose
        print progress output

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
        
        return
    

    def usage(self):
        
        print __doc__
        return


    def run(self):
        
        try:
            (opts, args) = getopt.getopt(self.argv[1:], 'c:p:i:o:hv', 
                            ['config=', 'packages=', 'id=', 'output=', 'help', 'verbose'])
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
                elif o in ('-v', '--verbose'):
                    self.isVerbose = True
                elif o in ('-h', '--help'):
                    self.usage()
                    return 0
                else:
                    assert False, 'option not handled'

            self.process()
            
        except ErrorWithDescription as err:
            print err
    
        finally: 
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
        
        print
        print "Create the build folders and the makefiles."
        print
        
        self.validate()
        
        packagesTreesList = self.loadPackagesTrees(self.packagesFilePathList)

        configTreesList = self.loadConfig(self.configFilePath)

        if self.isVerbose:
            print
            self.dumpTree(packagesTreesList, False)
        
            print
            self.dumpConfiguration(configTreesList)

        print
        self.loadConfiguration(configTreesList, self.desiredConfigurationId)

        if self.isVerbose:
            print
            self.dumpTree(packagesTreesList, True)

        if not os.path.isdir(self.outputFolder):
            os.makedirs(self.outputFolder)
                                       
        if self.isVerbose:
            print

        self.generatePreprocessorDefinitions(packagesTreesList, self.outputFolder)
        
        self.generateAllMakeFiles(packagesTreesList, self.outputFolder)
        
        return


    def generatePreprocessorDefinitions(self, packagesTreesList, outputFolder):
        
        headersDict = self.buildHeadersDict(packagesTreesList)
        for fileRelativePath in headersDict.iterkeys():
            
            fileAbsolutePath = os.path.join(outputFolder, fileRelativePath)
            if self.isVerbose:
                print fileAbsolutePath

            (folderAbsolutePath,_) = os.path.split(fileAbsolutePath)
            if not os.path.isdir(folderAbsolutePath):
                os.makedirs(folderAbsolutePath)
            
            # truncate existing files
            textFile = open(fileAbsolutePath, 'w')
            textFile.write('// {0}\n'.format(CommonApplication.getDoNotEditMessage()))
            headerLines = headersDict[fileRelativePath]
            for headerLine in headerLines:
                if self.isVerbose:
                    print headerLine
                textFile.write(headerLine)
                textFile.write('\n')
                
            textFile.close()

        if self.isVerbose:
            print
            
        return


    def generateAllMakeFiles(self, packagesTreesList, outputFolder):
        
        sourcesDict = self.buildSourcesDict(packagesTreesList)
        for folderRelativePath in sourcesDict.iterkeys():
            
            folderAbsolutePath = os.path.join(outputFolder, folderRelativePath)
            if not os.path.isdir(folderAbsolutePath):
                if self.isVerbose:
                    print('Creating folder \'{0}\''.format(folderAbsolutePath))
                os.makedirs(folderAbsolutePath)
            
            self.generateSubdirMk(folderAbsolutePath, sourcesDict, folderRelativePath)
            
        self.generateRootMakeFiles(sourcesDict, outputFolder)
            
        return

    
    def generateSubdirMk(self, folderAbsolutePath, sourcesDict, folderRelativePath):
        
        subdirAbsolutePath = os.path.join(folderAbsolutePath, 'subdir.mk')
        
        if self.isVerbose:
            if not os.path.isfile(subdirAbsolutePath):
                print('Writing file \'{0}\''.format(subdirAbsolutePath))
            else:
                print('Overwriting file \'{0}\''.format(subdirAbsolutePath))

        f = open(subdirAbsolutePath, 'w')
        
        self.generateDoNotEditMessage(f)
        f.write('# Add inputs and outputs from these tool invocations to the build variables\n')
        
        sources = sourcesDict[folderRelativePath]
        
        ccList = self.groupSourceFilesByType(sources, ['.c'])
        cppList = self.groupSourceFilesByType(sources, ['.cpp'])
        asmList = self.groupSourceFilesByType(sources, ['.S'])
        
        if len(ccList) > 0:
            f.write('C_SRCS += \\\n')
            
            i = 0
            for e in ccList:
                p = e['sourceAbsolutePath']
                f.write(self.expandPathSpaces(p))
                i+=1
                if i < len(ccList):
                    f.write(' \\')
                f.write('\n')
            f.write('\n')
        
        if len(cppList) > 0:
            f.write('CPP_SRCS += \\\n')
            
            i = 0
            for e in cppList:
                p = e['sourceAbsolutePath']
                f.write(self.expandPathSpaces(p))
                i+=1
                if i < len(cppList):
                    f.write(' \\')
                f.write('\n')                          
            f.write('\n')

        # TODO: process assembly files

        allList = []
        allList.extend(ccList)
        allList.extend(cppList)
        allList.extend(asmList)
         
        if len(allList) > 0:
            f.write('{0} += \\\n'.format('BCS'))
            
            i = 0
            for e in allList:
                fileNameComplete = e['fileName']
                (fileName, _) = os.path.splitext(fileNameComplete)
                p = os.path.join('.', folderRelativePath, '{0}.{1}'.format(fileName, 'bc'))
                f.write(self.expandPathSpaces(p))
                i+=1
                if i < len(allList):
                    f.write(' \\')
                f.write('\n')                          
            f.write('\n')

        if len(cppList) > 0:
            f.write('CPP_DEPS += \\\n')
            
            i = 0
            for e in cppList:
                fileNameComplete = e['fileName']
                (fileName, _) = os.path.splitext(fileNameComplete)
                p = os.path.join('.', folderRelativePath, '{0}.{1}'.format(fileName, 'd'))
                f.write(self.expandPathSpaces(p))
                i+=1
                if i < len(cppList):
                    f.write(' \\')
                f.write('\n')                          
            f.write('\n')

        if len(allList) > 0:
            f.write('# Each subdirectory must supply rules for building sources it contributes\n')
               
            for e in allList:
                fileNameComplete = e['fileName']
                (fileName, _) = os.path.splitext(fileNameComplete)
                p = os.path.join(folderRelativePath, '{0}.{1}'.format(fileName, 'bc'))
                sourceAbsolutePath = e['sourceAbsolutePath']
                f.write('{0}: {1}\n'.format(self.expandPathSpaces(p), self.expandPathSpaces(sourceAbsolutePath)))
                f.write('    @echo \'Building file: $<\'\n')
                
                fType = e['type']
                if fType == '.cpp':
                    toolName = 'clang++'
                    toolDesc = 'LLVM Clang++'
                elif fType == '.c':
                    toolName = 'clang'
                    toolName = 'LLVM Clang'
                
                f.write('    @echo \'Invoking: {0}\'\n'.format(toolDesc))
                
                f.write('    {0}'.format(toolName))
                f.write(' -DDEBUG=1')
                f.write(' -I"..."')
                f.write(' -O0 -emit-llvm -g3 -Wall -c -fmessage-length=0 -fsigned-char')
                f.write(' -MMD -MP -o "$@" "$<"')
                f.write('\n')
                
                f.write('    @echo \'Finished file: $<\'\n')
                f.write('    @echo \' \'\n')
                f.write('\n')
                                
        f.close()

        return
    

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
        

    def generateRootMakeFiles(self, sourcesDict, outputFolder):
        
        makefileAbsolutePath = os.path.join(outputFolder, 'makefile')
        
        if self.isVerbose:
            if not os.path.isfile(makefileAbsolutePath):
                print('Writing file \'{0}\''.format(makefileAbsolutePath))
            else:
                print('Overwriting file \'{0}\''.format(makefileAbsolutePath))

        f = open(makefileAbsolutePath, 'w')
        
        self.generateDoNotEditMessage(f)

        f.write('\n')
        f.write('-include ../makefile.init\n')        
        f.write('\n')
        f.write('-RM := {0} -rf\n'.format('rm'))        
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

        target = 'x.elf'
        
        f.write('# All Target\n')
        f.write('all: {0} secondary-outputs\n'.format(target))
        f.write('\n')

        f.write('# Tool invocations\n')
        f.write('{0}: $(BCS) $(USER_OBJS)\n'.format(target))
        f.write('    @echo \'Building target: $@\'\n')
        f.write('    @echo \'Invoking: {0}\'\n'.format('LLVM C++ linker'))
        f.write('    {0} -v -native -o "{1}" $(BCS) $(USER_OBJS) $(LIBS)\n'.format('clang++', target))
        f.write('    @echo \'Finishing building target: $@\'\n')
        f.write('    @echo \' \'\n')
        f.write('\n')

        f.write('# Other Targets\n')
        f.write('clean:\n')
        f.write('    -$(RM) $(BCS)$(CC_DEPS)$(CPP_DEPS)$(LLVM_BC_EXECUTABLES) {0}\n'.format(target))
        f.write('    @echo \' \'\n')
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
        
        objectsMkAbsolutePath = os.path.join(outputFolder, 'objects.mk')
        
        if self.isVerbose:
            if not os.path.isfile(objectsMkAbsolutePath):
                print('Writing file \'{0}\''.format(objectsMkAbsolutePath))
            else:
                print('Overwriting file \'{0}\''.format(objectsMkAbsolutePath))

        f = open(objectsMkAbsolutePath, 'w')
        
        self.generateDoNotEditMessage(f)

        f.write('USER_OBJS :=\n')
        f.write('\n')

        f.write('LIBS :=\n')
        f.write('\n')

        f.close()
        
        # ---------------------------------------------------------------------
        
        sourcesMkAbsolutePath = os.path.join(outputFolder, 'sources.mk')
        
        if self.isVerbose:
            if not os.path.isfile(sourcesMkAbsolutePath):
                print('Writing file \'{0}\''.format(sourcesMkAbsolutePath))
            else:
                print('Overwriting file \'{0}\''.format(sourcesMkAbsolutePath))

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
    
    