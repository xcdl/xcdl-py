# -*- coding: utf-8 -*-

"""
Usage:
    python -m ilg.xcdl.configMakefiles [options]

Options:
        
    -c, --config
        the root configuration file
        
    -v, --verbose
        print progress output

    -h, --help
        print this message
        
Purpose:
    Create the build folders and the makefiles.
    
"""

import getopt

from ilg.xcdl.commonApplication import CommonApplication
from ilg.xcdl.errorWithDescription import ErrorWithDescription


class Application(CommonApplication):
    
    def __init__(self, *argv):
                
        super(Application,self).__init__(*argv)

        # application specific members
        
        
        return
    

    def usage(self):
        
        print __doc__
        return


    def run(self):
        
        try:
            (opts, args) = getopt.getopt(self.argv[1:], 'c:hv', 
                            ['config=', 'help', 'verbose'])
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
                    self.treeFilePath = a
                elif o in ('-v', '--verbose'):
                    self.isVerbose = True
                elif o in ('-h', '--help'):
                    self.usage()
                    return 0
                else:
                    assert False, 'option not handled'
    
            #self.treeFilePath = '/Users/ilg/My Files/MacBookPro Vault/Projects/XCDL/Eclipse Workspaces/ws_tests/packages/meta/index.py'
            #self.treeFilePath = '/Users/ilg/My Files/MacBookPro Vault/Projects/XCDL/Eclipse Workspaces/ws_tests/packages/meta/master.py'
            self.process()
            
        except ErrorWithDescription as err:
            print err
    
        finally: 
            print   
            print '[done]'
            
        return 0        


    def process(self):
        
        print
        print "Create the build folders and the makefiles."
        print
        
        print 'Process root package "{0}"'.format(self.treeFilePath)
                
        self.loadPackagesTrees()
        
        return


    
        
    