# -*- coding: utf-8 -*-

"""
Usage:
    python -m ilg.xcdl.dumpConfig [options]

Options:
        
    -c, --config
        the root configuration file

    -p, --packages
        the root of the packages tree file, multiple trees accepted
        
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
        
        return
    

    def usage(self):
        
        print __doc__
        return

    def run(self):
        
        try:
            (opts, args) = getopt.getopt(self.argv[1:], 'c:p:hv', 
                            ['config=', 'packages=', 'help', 'verbose'])
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
        
        if self.treeFilePath == None:
            raise ErrorWithDescription('Missing --tree file path')

        return
    

    def process(self):
        
        print
        print "Dump the configuration tree."
        print
        
        print 'Process root package files {0}'.format(self.packagesFilePathList)
        packagesTreesList = self.loadPackagesTrees(self.packagesFilePathList)

        print 'Process config file "{0}"'.format(self.configFilePath)
        configTreesList = self.loadConfig(self.configFilePath)

        print
        self.dumpTree(packagesTreesList)
        
        print
        self.dumpConfiguration(configTreesList)

        return


    