# -*- coding: utf-8 -*-

# Copyright (C) 2012 Liviu Ionescu.
# This file is part of the XCDL project.

from ilg.xcdl.errorWithDescription import ErrorWithDescription

# -----------------------------------------------------------------------------

# Options and components have the bool flavour by default, but this can be 
# changed as desired. Packages always have the booldata flavour, and this 
# cannot be changed. Interfaces have the data flavour by default, since the 
# value of an interface is a count of the number of active and enabled 
# interfaces, but they can be given the bool or booldata flavours.

# -----------------------------------------------------------------------------

class Flavor(object):
    
    @staticmethod
    def construct(stringFlavor):
        
        if stringFlavor == 'none':
            return FlavorNone()
        elif stringFlavor == 'bool':
            return FlavorBool()
        elif stringFlavor == 'data':
            return FlavorData()
        elif stringFlavor == 'booldata':
            return FlavorBoolData()
        else:
            raise ErrorWithDescription('Unknown flavor {0}'.format(stringFlavor))
    
# -----------------------------------------------------------------------------

# The none is intended primarily for placeholder components in the hierarchy, 
# although it can be used for other purposes. Options with this flavour are 
# always enabled and do not have any additional data associated with them, 
# so there is no way for users to modify the option. For the purposes of 
# expression evaluation an option with flavour none always has the value 1. 
# Normal #define processing will take place, so typically a single #define 
# will be generated using the option name and a value of 1. Similarly 
# build-related properties such as compile will take effect.

class FlavorNone(object):
    
    def __init__(self):
        
        self._isEnabled = True
        self._value = '1'
        return
    
        
    def getName(self):
        
        return 'none'

    
    def getValue(self):
        
        if self._isEnabled:
            return self._value
        else:
            return '0'

    
    def isEnabled(self):
        
        return self._isEnabled
    
    
# -----------------------------------------------------------------------------

# Boolean options can be either enabled or disabled, and there is no 
# additional data associated with them. If a boolean option is disabled 
# then no #define will be generated and any build-related properties such 
# as compile will be ignored. For the purposes of expression evaluation a 
# disabled option has the value 0. If a boolean option is enabled then 
# normal #define processing will take place, all build-related properties 
# take effect, and the option’s value will be 1.

class FlavorBool(FlavorNone):
    
    def __init__(self):
                
        super(FlavorBool, self).__init__()

        return


    def getName(self):
        
        return 'bool'
    
    
    def setIsEnabled(self, isEnabled=True):
        
        self._isEnabled = isEnabled
    
 
# -----------------------------------------------------------------------------

# Options with this flavour are always enabled, and have some additional data 
# associated with them which can be edited by the user. This data can be any 
# sequence of characters, although in practice the legal_values property 
# will often be used to impose constraints. In appropriate contexts such as 
# expressions the configuration tools will attempt to interpret the data 
# as integer or floating point numbers. Since an option with the data flavour 
# cannot be disabled, normal #define processing takes place and the data 
# will be used for the value. Similarly all build-related properties take 
# effect, and the option’s value for the purposes of expression evaluation 
# is the data.

class FlavorData(FlavorNone):
    
    def __init__(self):
                
        super(FlavorData, self).__init__()
        
        return


    def getName(self):
        
        return 'data'
    
    
    def setValue(self, value):
        
        self._value = value
        return


# -----------------------------------------------------------------------------

# This combines the bool and data flavours. The option may be enabled or 
# disabled, and in addition the option has some associated data. If the 
# option is disabled then no #define will be generated, the build-related 
# properties have no effect, and for the purposes of expression evaluation 
# the option’s value is 0. If the option is enabled then a #define will be 
# generated using the data as the value, all build-related properties take 
# effect, and the option’s value for the purposes of expression evaluation 
# is the data. If 0 is legal data then it is not possible to distinguish 
# this case from the option being disabled or inactive.

class FlavorBoolData(FlavorData):

    def __init__(self):
                
        super(FlavorBoolData, self).__init__()
                
        return


    def getName(self):
        
        return 'booldata'
    
    
    def setIsEnabled(self, isEnabled=True):
        
        self._isEnabled = isEnabled
