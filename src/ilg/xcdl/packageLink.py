# -*- coding: utf-8 -*-

class PackageLink(object):
    
    _linksList = []
    
    def __init__(self, filePath):
             
        PackageLink._linksList.append(filePath)
        return

    @staticmethod
    def cleanList():
        
        PackageLink._linksList = []
        
    @staticmethod
    def getLinks():
        
        return PackageLink._linksList

    
class PackagesBasePath(object):
    
    _basePath = None
    
    def __init__(self, basePath):
             
        if PackagesBasePath._basePath == None:
            PackagesBasePath._basePath = basePath
        else:
            print 'PackageBasePath redefined'
            
        return

    @staticmethod
    def clean():
        
        PackagesBasePath._basePath = None
        
    @staticmethod
    def get():
        
        return PackagesBasePath._basePath
