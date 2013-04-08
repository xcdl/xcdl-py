# -*- coding: utf-8 -*-

"""
Usage:
    sh xcdlBuild.sh [params]
    python -m ilg.xcdl.build [params]

Params:
        
    -r, --repository
        the relative/absolute path to the repository folder;
        multiple repositories accepted. (mandatory)
    
    -c, --build_config
        the name of the build configuration to be generated; can be only a 
        leaf node. (mandatory)

    -b, --build_dir
        the output folder, where the build configurations will be created.
        (mandatory)
        
    -l, --linearise
        linearise the build subfolder to shorten the path. (default=True)
        
    -a, --always
        always generate the build tree, regardless of the timestamps
        
    -Wm,...
        'make' arguments pass arguments to make

    -Wr,...
        'run' arguments (copy them to makefile)
        
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
import sys
import traceback

from ilg.xcdl.commonApplication import CommonApplication
from ilg.xcdl.errorWithDescription import ErrorWithDescription
from ilg.xcdl.errorWithDescription import ErrorWithoutDescription


class Application(CommonApplication):
    
    def __init__(self, *argv):
                
        super(Application, self).__init__(*argv)

        # application specific members

        self.packagesAbsolutePathList = []
        
        self.configFilePath = None
        
        self.desiredConfigurationName = None
        
        self.outputFolder = 'build'
        
        self.doLinearise = True
        
        self.makeArguments = []
        self.makeTarget = 'all'

        self.runArguments = []
        
        self.ignoreTimestamps = False
        
        # Not used, but should be present as None
        self.toolchainId = None
        
        return
    

    def usage(self):
        
        print __doc__
        return


    def run(self):
        
        try:
            (opts, args) = getopt.getopt(self.argv[1:], 'r:c:b:lW:hva',
                            [ 'repository=', 'build_config=', 'build_dir=',
                             'linearise', 'help', 'verbose', 'always'])
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err)  # will print something like "option -a not recognised"
            self.usage()
            return 2
        
        retval = 0
        try:
            if len(args) == 1:
                self.makeTarget = args[0]
            elif len(args) > 0:
                print 'Unused arguments: '
                for arg in args:
                    print '\t{0}'.format(arg)
                self.usage()
                return 2
                    
            for (o, a) in opts:
                # a = a
                if o in ('-r', '--repository'):
                    self.packagesAbsolutePathList.append(a)
                elif o in ('-c', '--build_config'):
                    self.desiredConfigurationName = a
                elif o in ('-b', '--build_dir'):
                    self.outputFolder = a
                elif o in ('-l', '--linearise'):
                    self.doLinearise = True
                elif o in ('-a', '--always'):
                    self.ignoreTimestamps = True
                elif o in ('-v', '--verbose'):
                    self.verbosity += 1
                elif o in ('-h', '--help'):
                    self.usage()
                    return 0
                elif o in ('-W'):
                    aa = a.split(',')
                    if aa[0] == 'm':
                        self.makeArguments = aa[1:]
                    elif aa[0] == 'r':
                        self.runArguments = aa[1:]
                    else:
                        assert False, 'option -W{0} not handled'.format(a)
                elif o in ('all', 'clean'):
                    #print o
                    pass
                else:
                    assert False, 'option not handled'

            CommonApplication.setVerbosity(self.verbosity)
            retval = self.process()

        except Exception:
            traceback.print_exc(file=sys.stdout)
            traceback.print_exc()
            retval = 3

        except ErrorWithoutDescription as err:
            retval = 1
            
        except ErrorWithDescription as err:
            print 'ERROR: {0}'.format(err)
            retval = 1

        finally:
            if self.verbosity > 0:
                print   
                print '[done]'
            
        return retval        


    def validate(self):
        
        if len(self.packagesAbsolutePathList) == 0:
            raise ErrorWithDescription('Missing mandatory --repository parameter')
            
        if self.desiredConfigurationName == None:
            raise ErrorWithDescription('Missing mandatory --build_config parameter')
                                
        return


    def process(self):

        startTime = time.time()
        
        if self.verbosity > 0:
            print
            print '* The \'xcdlBuild\' tool (part of the XCDL framework) *'
            print 'Process component repositories, create the GNU Make files and execute them.'
            print
            if self.verbosity > 1:
                print 'Verbosity level {0}'.format(self.verbosity)
                print
        
        self.validate()
        
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

        # TODO: consider original copyFiles time
        
        if not self.ignoreTimestamps and rootMakeFileUpdateTime > CommonApplication.maxScriptUpdateTime:
            if self.verbosity > 0:
                print
                print 'The XCDL files did not change since last build, no need to recreate the build tree.'
        else:
            toolchainNode = self.processAndCreate(repositoriesList, configNode, outputSubFolder, toolchainNode)      
        
        stopTime = time.time()
        print
        print 'XCDL metadata processed in {0}.'.format(
                        self.convertTimeDifferenceToString(stopTime - startTime))

        buildFolderAbsolutePath = os.path.join(self.outputFolder, outputSubFolder)
        ret = self.executeBuild(configNode, buildFolderAbsolutePath, toolchainNode)
        return ret


    def processAndCreate(self, repositoriesList, configNode, outputSubFolder, toolchainNode):
        
        if self.verbosity > 0:
            print
        configNode = self.loadBuildConfiguration(configNode, 0)

        # enable configuration nodes too, for a more uniform processing
        # (of CopyFiles, for example)
        configNode.setIsEnabledWithCountRecursive()
        
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
            raise ErrorWithDescription('Error or requirement not satisfied, cannot continue')
        elif count > 1:
            raise ErrorWithDescription('Errors or requirements not satisfied, cannot continue')

        if self.verbosity > 1:
            print
            self.dumpTree(repositoriesList, True)

        if not os.path.isdir(self.outputFolder):
            os.makedirs(self.outputFolder)
                                               
        # print outputSubFolder

        CommonApplication.clearErrorCount()
        if self.verbosity > 0:
            print
            print 'Generate header files...'
        self.generatePreprocessorDefinitions(repositoriesList, self.outputFolder, outputSubFolder)
        
        if self.verbosity > 0:
            print
            print 'Copy custom files...'
        self.copyCustomFiles(repositoriesList, configNode, self.outputFolder, outputSubFolder)

        if self.verbosity > 0:
            print
            print 'Using toolchain \'{0}\'.'.format(toolchainNode.getName())
            
        if self.verbosity > 0:
            print
            print 'Generate GNU Make files...'
            
        # 'makefile' must be the last file written
        self.generateAllMakeFiles(repositoriesList, configNode, toolchainNode, self.outputFolder, outputSubFolder)
        
        count = CommonApplication.getErrorCount()
        if count > 0:
            raise ErrorWithoutDescription()
        
        return toolchainNode


    def executeBuild(self, configNode, buildFolderAbsolutePath, toolchainNode):
        
        print
        if self.verbosity > 0:
            print 'Configuration \'{0}\'.'.format(configNode.getName())
            print 'Eclipse build configuration \'{0}\'.'.format(self.desiredConfigurationName)
            print
        
        startTime = time.time()
        print 'XCDL build started, using toolchain \'{0}\'...'.format(toolchainNode.getName())
        print
        
        print 'cd {0}'.format(buildFolderAbsolutePath)
        os.chdir(buildFolderAbsolutePath)
        
        # TODO: get this from an external location 
        toolchainBinAbsolutePath = None  # '/opt/local/bin'
        
        env = os.environ
        path = env['PATH']
        # print 'PATH={0}'.format(path)
        pathElements = path.split(':')
        if (toolchainBinAbsolutePath != None) and (toolchainBinAbsolutePath not in pathElements):
            pathElements.append(toolchainBinAbsolutePath)
            
        newPath = ':'.join(pathElements)
        env['PATH'] = newPath
        print 'PATH={0}'.format(newPath)
        print

        #print self.makeArguments
        
        makeCommand = ['make']
        makeCommand.extend(self.makeArguments)
        makeCommand.append(self.makeTarget)
        
        print ' '.join(makeCommand)
        
        sys.stdout.flush()
        sys.stderr.flush()
        ret = os.spawnvpe(os.P_WAIT, makeCommand[0], makeCommand, env)
        sys.stdout.flush()
        sys.stderr.flush()
        
        stopTime = time.time()
        print 'XCDL build completed in {0}.'.format(
                        self.convertTimeDifferenceToString(stopTime - startTime))
        
        sys.stdout.flush()
        return ret

    def convertTimeDifferenceToString(self, timeDifference):
        
        if timeDifference < 1:
            # change unit to millisecond
            timeDifference *= 1000
            
            return '{0:d}ms'.format(int(timeDifference))
        
        return '{0:.3f}s'.format(timeDifference)
