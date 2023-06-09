#!/usr/bin/env python3

from communication.arguments.Comparison import Comparison
from communication.arguments.CoupleValue import CoupleValue
from communication.preferences.Value import Value
from communication.preferences.Preferences import Preferences

class Argument:
    """
    Argument class.
    This class implements an argument used in the negotiation.

    attr:
        decision:
        item:
        comparison_list:
        couple_values_list:
    """

    def __init__(self, boolean_decision, item):
        """
        Creates a new Argument.
        """
        self.__decision = boolean_decision
        self.__item = item.get_name()
        self.__comparison_list = []
        self.__couple_values_list = []
        self.__counter_arguments = []

    def get_comparison_list(self):
        return(self.__comparison_list)

    def get_couple_values_list(self):
        return(self.__couple_values_list)
        
    def __str__(self):
        res = self.__item.__str__() + " <- "
        first = True
        for arg in self.get_comparison_list() + self.get_couple_values_list():
            if first:
                first = False
            else:
                res += ", "
            res += arg.__str__()
        return res

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """
        Adds a premiss comparison in the comparison list.
        """
        self.__comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    def add_premiss_couple_values(self, criterion_name, value):
        """
        Add a premiss couple values in the couple values list.
        """
        self.__couple_values_list.append(CoupleValue(criterion_name, value))

    def List_supporting_proposal(self, item, preferences):
        """
        Generate a list of premisses which can be used to support an item :param item: Item - name of the item
        return: list of all premisses PRO an item (sorted by order of importance based on agent’s preferences) 
        """
        premisses = []
        for criteria in preferences.get_criterion_name_list():
            value = preferences.get_value(item, criteria)
            good_enough_values = [Value.VERY_GOOD, Value.GOOD]
            if value in good_enough_values:
                premisses.append(criteria)
        return premisses

    def List_attacking_proposal(self, item, preferences):
        """
        Generate a list of premisses which can be used to attack an item :param item: Item - name of the item
        return: list of all premisses CON an item (sorted by order of importance based on agent’s preferences) 
        """
        premisses = []
        for criteria in preferences.get_criterion_name_list():
            value = preferences.get_value(item, criteria)
            bad_enough_values = [Value.VERY_BAD, Value.BAD]
            if value in bad_enough_values:
                premisses.append(criteria)
        return premisses
    
    def add_counter_argument(self, counter_arg):
        self.counter_arguments.append(counter_arg)

    def get_counter_arguments(self):
        return self.__counter_arguments

    def get_item(self):
        return self.__item

    def get_decision(self):
        return self.__decision

    def get_premisces(self):
        return self.get_comparison_list() + self.get_couple_values_list()