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
            print 'Process the \'requirements\' properties...'
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


