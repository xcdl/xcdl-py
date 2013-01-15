# -*- coding: utf-8 -*-

"""
Usage:
    python -m ilg.xcdl.dumpConfig [options]

Options:
        
    -c, --config
        the root configuration file

    -p, --packages
        the root of the packages tree file, multiple trees accepted
    
    -i, --id
        the ID of the configuration to be generated
        
    -v, --verbose
        print progress output

    -h, --help
        print this message
        
Purpose:
    Dump the configuration tree.
    
"""

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
        
        return
    

    def usage(self):
        
        print __doc__
        return


    def run(self):
        
        try:
            (opts, args) = getopt.getopt(self.argv[1:], 'c:p:i:hv', 
                            ['config=', 'packages=', 'id=', 'help', 'verbose'])
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err) # will print something like "option -a not recognised"
            self.usage()
            return 2
        
        retval = 0
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
                    self.packagesAbsolutePathList.append(a)
                elif o in ('-i', '--id'):
                    self.desiredConfigurationId = a
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
            print   
            print '[done]'
            
        return retval        


    def process(self):
        
        print
        print '* The dumpConfig tool (part of the XCDL framework) *'
        print "* Dump the configuration trees *"
        print
        if self.verbosity > 1:
            print 'Verbosity level {0}'.format(self.verbosity)
            print
        
        repoFolderAbsolutePathList = []
        if self.configFilePath != None:
            (configTreesList,repoFolderAbsolutePathList) = self.parseConfigurationFile(self.configFilePath, -1)
            self.packagesAbsolutePathList.extend(repoFolderAbsolutePathList)
            
        print
        repositoriesList = self.parseRepositories(self.packagesAbsolutePathList, -1)

        print
        self.dumpTree(repositoriesList, False)
        
        if self.configFilePath != None:
            print
            self.dumpConfiguration(configTreesList)

        if self.desiredConfigurationId != None:
            print
            configNode = self.loadConfiguration(configTreesList, self.desiredConfigurationId, -1)

            print
            print 'Build preprocessor symbols dictionary...'
            count = self.processSymbolsDict(repositoriesList)
            print '- {0} symbol(s) processed.'.format(count)

            print
            print 'Process initial \'isEnabled\' properties'
            self.processInitialIsEnabled(repositoriesList)
            
            print
            print 'Process \'requires\' properties'
            self.processRequiresProperties(repositoriesList, configNode, False)
            
            CommonApplication.clearErrorCount()
            self.processRequiresProperties(repositoriesList, configNode, False)
            count = CommonApplication.getErrorCount()
            if count > 0:
                print '{0} error(s) encountered'.format(count)
            
            print
            self.dumpTree(repositoriesList, True)
                  
            print
            self.dumpPreprocessorDefinitions(repositoriesList) 
            
            print 
            self.dumpSourceFiles(repositoriesList)
            
        return



    