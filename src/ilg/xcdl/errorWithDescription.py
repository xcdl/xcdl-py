# -*- coding: utf-8 -*-

class ErrorWithDescription(Exception):

    def __init__(self, descriptionString):
        self.descriptionString = descriptionString
        
    def __str__(self):
        return self.descriptionString
    

class ErrorWithoutDescription(Exception):

    def __init__(self):
        pass
        
    def __str__(self):
        return 'ErrorWithoutDescription'
    