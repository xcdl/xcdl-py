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
        
        self.generateMakefiles(packagesTreesList, self.outputFolder)
        
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


    def generateMakefiles(self, packagesTreesList, outputFolder):
        
        sourcesDict = self.buildSourcesDict(packagesTreesList)
        for folderRelativePath in sourcesDict.iterkeys():
            
            folderAbsolutePath = os.path.join(outputFolder, folderRelativePath)
            if not os.path.isdir(folderAbsolutePath):
                os.makedirs(folderAbsolutePath)
            
            subdirAbsolutePath = os.path.join(folderAbsolutePath, 'subdir.mk')
            subdirFile = open(subdirAbsolutePath, 'w')
            subdirFile.write('# {0}\n'.format(CommonApplication.getDoNotEditMessage()))
            
            sources = sourcesDict[folderRelativePath]
            if self.isVerbose:
                print folderRelativePath
                
            for source in sources:
                if self.isVerbose:
                    print source
    
            subdirFile.close()
            
        return
    
    