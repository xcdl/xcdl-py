# -*- coding: utf-8 -*-

"""
Usage:
    sh xcdlBuild.sh [params]
    python -m ilg.xcdl.build [params]

Params:
        
    -r, --repository
        the relative/absolute path to the repository folder;
        multiple repositories accepted. (mandatory)
    
    -n, --name
        the name of the build configuration to be generated; can be only a 
        leaf node. (mandatory)

    -b, --build
        the output folder, where the build configurations will be created.
        (mandatory)
        
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
import time

from ilg.xcdl.commonApplication import CommonApplication
from ilg.xcdl.errorWithDescription import ErrorWithDescription


class Application(CommonApplication):
    
    def __init__(self, *argv):
                
        super(Application, self).__init__(*argv)

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
            (opts, args) = getopt.getopt(self.argv[1:], 'r:n:b:lhv',
                            [ 'repository=', 'name=', 'build=',
                             'linearise', 'help', 'verbose'])
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err)  # will print something like "option -a not recognised"
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
                # a = a
                if o in ('-r', '--repository'):
                    self.packagesAbsolutePathList.append(a)
                elif o in ('-n', '--name'):
                    self.desiredConfigurationName = a
                elif o in ('-b', '--build'):
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
            print 'ERROR: {0}'.format(err)
            retval = 1
    
        finally:
            if self.verbosity > 0:
                print   
                print '[done]'
            
        return retval        


    def validate(self):
        
        if self.desiredConfigurationName == None:
            raise ErrorWithDescription('Missing mandatory --name= parameter')

        if self.outputFolder == None:
            raise ErrorWithDescription('Missing mandatory --build= parameter')
                                
        return


    def process(self):
        
        if self.verbosity > 0:
            print
            print '* The xcdlBuild tool (part of the XCDL framework) *'
            print '* Create the distributed GNU Make files and build *'
            print
            if self.verbosity > 1:
                print 'Verbosity level {0}'.format(self.verbosity)
                print
        
        self.validate()
        
        if self.verbosity > 0:
            print
        repositoriesList = self.parseRepositories(self.packagesAbsolutePathList, 0)

        if self.verbosity > 0:
            print             
            print 'Latest XCDL files modified time: {0}'.format(time.ctime(CommonApplication.maxScriptUpdateTime))

        if self.verbosity > 1:
            print
            self.dumpTree(repositoriesList, False)

        configNode = self.getBuildConfigurationNode(self.desiredConfigurationName)

        outputSubFolder = configNode.getBuildFolderRecursiveWithSubstitutions()
        if self.doLinearise:
            outputSubFolder = outputSubFolder.replace(os.sep, '_')

        rootMakeFileUpdateTime = self.getRootMakeFileUpdateTime(self.outputFolder, outputSubFolder)
        if self.verbosity > 0:
            print 'Root makefile modified time: {0}'.format(time.ctime(rootMakeFileUpdateTime))
        
        (toolchainNode, _) = self.validateToolchain(configNode)

        if rootMakeFileUpdateTime > CommonApplication.maxScriptUpdateTime:
            if self.verbosity > 0:
                print
                print 'XCDL files did not change since last build, no need to recreate the build tree.'
        else:
            toolchainNode = self.processAndCreate(repositoriesList, configNode, outputSubFolder, toolchainNode)      
        
        buildFolderAbsolutePath = os.path.join(self.outputFolder, outputSubFolder)
        self.executeBuild(configNode, buildFolderAbsolutePath, toolchainNode)
        return


    def processAndCreate(self, repositoriesList, configNode, outputSubFolder, toolchainNode):
        
        if self.verbosity > 0:
            print
        configNode = self.loadBuildConfiguration(configNode, 0)

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
                                               
        # print outputSubFolder

        if self.verbosity > 0:
            print
            print 'Generate header files...'
        self.generatePreprocessorDefinitions(repositoriesList, self.outputFolder, outputSubFolder)
        
        if self.verbosity > 0:
            print
            print 'Using toolchain \'{0}\'.'.format(toolchainNode.getName())
            
        if self.verbosity > 0:
            print
            print 'Generate GNU Make files...'
        self.generateAllMakeFiles(repositoriesList, configNode, toolchainNode, self.outputFolder, outputSubFolder)
        
        return toolchainNode


    def executeBuild(self, configNode, buildFolderAbsolutePath, toolchainNode):
        
        print
        print '**** XCDL configuration \'{0}\' ****'.format(configNode.getName())
        print '**** Eclipse build configuration \'{0}\' ****'.format(self.desiredConfigurationName)
        print '**** Toolchain \'{0}\' ****'.format(toolchainNode.getName())
        
        startTime = time.time()
        print '**** {0} XCDL build started ****'.format(
                        time.strftime('%H:%M:%S', time.localtime(startTime)))
        print
        print 'cd {0}'.format(buildFolderAbsolutePath)
        os.chdir(buildFolderAbsolutePath)
        
        # TODO: get this from an external location 
        toolchainBinAbsolutePath = '/opt/local/bin'
        
        env = os.environ
        path = env['PATH']
        # print 'PATH={0}'.format(path)
        pathElements = path.split(':')
        if (toolchainBinAbsolutePath != None) and (toolchainBinAbsolutePath not in pathElements):
            pathElements.append(toolchainBinAbsolutePath)
            
        newPath = ':'.join(pathElements)
        env['PATH'] = newPath
        print 'PATH={0}'.format(newPath)
        
        print 'make all'
        os.spawnvpe(os.P_WAIT, 'make', ['make', 'all'], env)
        
        stopTime = time.time()
        print
        print '**** {0} Build finished (took {1:.3f}s) ****'.format(
                        time.strftime('%H:%M:%S', time.localtime(stopTime)),
                        stopTime - startTime)
        
        return
