from mesa import Model
from mesa.time import RandomActivation
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Value import Value
from communication.arguments.Argument import Argument

import random


class ArgumentAgent(CommunicatingAgent):
    """ 
    ArgumentAgent which inherit from CommunicatingAgent .
    """
    def __init__(self, unique_id, model, name, preferences):
        super().__init__(unique_id, model, name)
        self.preference = self.generate_preferences(preferences)
        self.preference_dict = preferences

    def step(self):
        new_messages = set(self.get_new_messages())

        if new_messages:

            # If the agent receives a PROPOSE
            new_propose = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.PROPOSE))
                )
            if new_propose:
                for mess in new_propose:
                    is_in_preferred = self.get_preference().is_item_among_top_10_percent(
                        mess.get_content(), list(self.get_preference_dict().keys())
                        )
                    if is_in_preferred:
                        self.send_specific_message(mess, MessagePerformative.ACCEPT)
                    else:
                        self.send_specific_message(mess, MessagePerformative.ASK_WHY)

            # If the agent receives an ACCEPT
            new_accept = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.ACCEPT))
                )
            if new_accept:
                for mess in new_accept:
                    item = mess.get_content()
                    if item in self.get_preference_dict().keys():
                        self.send_specific_message(
                            mess, MessagePerformative.COMMIT)
                        self.remove_item(item)
                        
            # If the message is a ASK_WHY
            new_ask_why = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.ASK_WHY))
                )
            if new_ask_why:
                for mess in new_ask_why:
                    self.send_specific_message(mess, MessagePerformative.ARGUE)

            # If the agent receives a COMMIT
            new_commit = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.COMMIT))
                )
            if new_commit:
                for mess in new_commit:
                    item = mess.get_content()
                    if item in self.get_preference_dict().keys():
                        self.send_specific_message(
                            mess, MessagePerformative.COMMIT)
                        self.remove_item(item)

    def get_preference(self):
        return self.preference

    def get_preference_dict(self):
        return self.preference_dict

    def remove_item(self, item):
        self.get_preference_dict().pop(item)
        self.get_preference().remove_item(item)

    def generate_preferences(self, List_items):
        for item in List_items:
            pref = Preferences()
            pref.set_criterion_name_list(List_items[item].keys())
            for criteria in List_items[item]:
                pref.add_criterion_value(CriterionValue(
                    item, criteria, List_items[item][criteria]))
        return pref

    def send_specific_message(self, message_received, performative):
        sender = message_received.get_exp()
        content = message_received.get_content()
        if performative.__str__() == "PROPOSE":
            new_content = content
        elif performative.__str__() == "ACCEPT":
            new_content = content
        elif performative.__str__() == "ASK_WHY":
            new_content = content
        elif performative.__str__() == "COMMIT":
            new_content = content
        elif performative.__str__() == "ARGUE":
            new_content = ""
        message = Message(self.get_name(), sender,
                          performative, new_content)
        self.send_message(message)
        print(message.__str__())


class ArgumentModel (Model):
    """ 
    ArgumentModel which inherit from Model .
    """

    def __init__(self, n_agent, preferences):
        super().__init__()
        self.n_agent = n_agent
        self.preferences = preferences
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        # Initialize agents
        self.agents = self.initialize_agents()
        
        self.running = True
        self.current_step = 0

    def initialize_agents(self):
        agents = []
        for idx in range(self.n_agent):
            agents.append(ArgumentAgent(idx, self, f"A{idx}", self.preferences[idx]))
            print(f"L'agent {agents[idx].get_name()} a été créé")
            self.schedule.add(agents[idx])
        
        return agents

    def step(self):
        self.current_step += 1
        self.__messages_service.dispatch_messages()
        self.schedule.step()


def run_argumentation():
    """
    Function to run a specific argumentation protocole.
    """
    # Initialize objects
    diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
    electric_engine = Item("Electric Engine", "A very quiet engine")

    # Set agent preferences
    agent_0_preferences = {
        diesel_engine: {
        CriterionName.PRODUCTION_COST: Value.VERY_GOOD,
        CriterionName.ENVIRONMENT_IMPACT: Value.VERY_BAD,
        CriterionName.CONSUMPTION: Value.GOOD,
        CriterionName.DURABILITY: Value.VERY_GOOD,
        CriterionName.NOISE: Value.BAD
        },
        electric_engine: {
        CriterionName.PRODUCTION_COST: Value.BAD,
        CriterionName.ENVIRONMENT_IMPACT: Value.VERY_GOOD,
        CriterionName.CONSUMPTION: Value.VERY_BAD,
        CriterionName.DURABILITY: Value.GOOD,
        CriterionName.NOISE: Value.VERY_GOOD
        }
        }
    agent_1_preferences = {
        diesel_engine: {
        CriterionName.PRODUCTION_COST: Value.GOOD,
        CriterionName.ENVIRONMENT_IMPACT: Value.BAD,
        CriterionName.CONSUMPTION: Value.GOOD,
        CriterionName.DURABILITY: Value.VERY_BAD,
        CriterionName.NOISE: Value.VERY_BAD
        },
        electric_engine: {
        CriterionName.PRODUCTION_COST: Value.GOOD,
        CriterionName.ENVIRONMENT_IMPACT: Value.BAD,
        CriterionName.CONSUMPTION: Value.BAD,
        CriterionName.DURABILITY: Value.VERY_GOOD,
        CriterionName.NOISE: Value.VERY_GOOD
        }
        }

    # Initialize the model
    argument_model = ArgumentModel(2, [agent_0_preferences, agent_1_preferences])
    print("AGENT FROM MODEL : ",argument_model.agents)

    # Retrieve agents
    Buyer = argument_model.agents[0]
    Seller = argument_model.agents[1]

    # Launch the Communication
    message = Message("A0", "A1", MessagePerformative.PROPOSE, electric_engine)
    #message = Message("A0", "A1", MessagePerformative.PROPOSE, diesel_engine)
    print(message.__str__())
    Buyer.send_message(message)

    step = 0
    while step < 100:
        argument_model.step()
        step += 1


if __name__ == "__main__":
    run_argumentation()