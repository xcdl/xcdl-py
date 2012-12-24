# -*- coding: utf-8 -*-

class PackageLocation():
    
    
    def __init__(self, folderAbsolutePath, scriptAbsolutePath):
        
        self._folderAbsolutePath = folderAbsolutePath
        self._scriptAbsolutePath = scriptAbsolutePath
        
        return
    

    def getFolderAbsolutePath(self):
        
        return self._folderAbsolutePath
    
    
    def getScriptAbsolutePath(self):
        
        return self._scriptAbsolutePath
    
    