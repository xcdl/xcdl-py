# -*- coding: utf-8 -*-

class ErrorWithDescription(Exception):

    def __init__(self, descriptionString):
        self.descriptionString = descriptionString
        
    def __str__(self):
        return self.descriptionString
    