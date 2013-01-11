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
        
        self.packagesFilePathList = []
        
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
                elif o in ('-v', '--verbose'):
                    self.verbosity = True
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
            raise ErrorWithDescription('Missing --packages files')
        
        return
    

    def process(self):
        
        self.validate()
        
        print
        print "Dump the configuration tree."
        print
        
        packagesTreesList = self.processPackagesTrees(self.packagesFilePathList)

        if self.configFilePath != None:
            configTreesList = self.processConfigFile(self.configFilePath)

        print
        self.dumpTree(packagesTreesList, False)
        
        if self.configFilePath != None:
            print
            self.dumpConfiguration(configTreesList)

        if self.desiredConfigurationId != None:
            print
            self.loadConfiguration(configTreesList, self.desiredConfigurationId)

            print
            self.processInitialIsEnabled(packagesTreesList)
            
            print
            self.dumpTree(packagesTreesList, True)
                  
            print
            self.dumpPreprocessorDefinitions(packagesTreesList) 
            
            print 
            self.dumpSourceFiles(packagesTreesList)
            
        return



    