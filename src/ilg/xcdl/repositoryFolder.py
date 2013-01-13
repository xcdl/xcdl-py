# -*- coding: utf-8 -*-


class RepositoryFolder():
    
    
    # static member
    _objectsList = None

    
    @staticmethod
    def setList(oList):
        
        RepositoryFolder._objectsList = oList
        return


    @staticmethod    
    def getList():
        
        return RepositoryFolder._objectsList


    def __init__(self, folderPath):
        
        self._folderPath = folderPath

        # if the static list is defined, add object to the list
        if RepositoryFolder._objectsList != None:
            RepositoryFolder._objectsList.append(self)

        return
    

    def getFolderPath(self):
        
        return self._folderPath
    
    