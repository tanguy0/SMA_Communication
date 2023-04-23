#!/usr/bin/env python3


class CoupleValue:
    """
    CoupleValue class.
    This class implements a couple value used in argument object.

    attr:
        criterion_name:
        value:
    """

    def __init__(self, criterion_name, value):
        """
        Creates a new couple value.
        """
        self.__criterion_name = criterion_name
        self.__value = value
    
    def get_criterion_name(self):
        return self.criterion_name

    def get_value(self):
        return self.value

    def __str__(self):
        #return f"{self.__criterion_name.name} = {self.__value}"
        return f"{self.__criterion_name} = {self.__value}"
