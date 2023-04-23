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
        self.preference = Preferences()
        self.generate_preferences(preferences)
        self.preference_dict = preferences
        
    def get_preference(self):
        """ "
        input: None
        output: Preference data with structure:
                        {item1:{crit1:value1,
                                crit2:val2...},
                        item2: ...,
                        "crit_order": [c1, ci, ]}
                        where the agents preferes c1 > ci ...
        """
        return self.preference

    def get_preference_dict(self):
        """ "
        input: None
        output: dict object
        """
        return self.preference_dict

    def get_model(self):
        """
        input: None
        Ouptut: ArgumentObject object
        """
        return self.model
    
    def get_item_list(self):
        """
        input: None
        Output: list object, all the items know to the agent
        """
        item_list = self.get_preference_dict().keys()
        return item_list

    def get_criteria_from_name(self, criteria_name):
        """
        input:
            criteria_name: string object, name of a criteria (eg: PRODUCTION_COST)
        output: CriterionName object, corresponding to criteria_name
        """
        for crit in CriterionName:
            if crit.__str__() == criteria_name:
                return crit

    def get_value_from_name(self, value_name):
        """
        input:
            value_name: string object, name of a value (eg: VERY_BAD)
        output: Value object, corresponding to value_name
        """
        for val in Value:
            for val in Value:
                if val.__str__() == value_name:
                    return val

    def get_item_from_name(self, item_name):
        """
        input:
            item_name: string object, name of an item (eg: "DIESEL ENGINE")
        output: Item object, corresponding to item_name
        """
        for item in self.get_preference_dict().keys():
            
            if item_name.__str__() == item.__str__():
                return item

    def step(self):
        new_messages = set(self.get_new_messages())
        print("NEW_MESSAGE : ",new_messages)

        if new_messages:
            # ARGUE MESSAGE RECEIVED
            new_argue = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.ARGUE))
            )
            if new_argue:
                for mess in new_argue:
                    other_agent = mess.get_exp()
                    # argument_parsing function gets a previous message and retrieves the item in negociation
                    # and the arguments used in favor or against the discussed item
                    item, previous_premise, rebutal = self.argument_parsing(
                        mess.get_content()
                    )
                    # update_argument builds the defense or the attack of the discussed item, wrt the previous
                    # one being a rebutal or not
                    new_premise, conclusion = self.update_argument(
                        item, previous_premise, other_agent, rebutal
                    )
                    if conclusion:
                        self.send_specific_message(
                            mess, MessagePerformative.ACCEPT, rebutal=True
                        )
                    else:
                        self.send_specific_message(
                            mess,
                            MessagePerformative.ARGUE,
                            rebutal=True,
                            premise=new_premise,
                        )

            # ASK WY MESSAGE RECEIVED
            new_ask_why = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.ASK_WHY))
            )
            if new_ask_why:
                for mess in new_ask_why:
                    # send_specific_message in the "ARGUE" case (when its the first argue for a specific item)
                    # also build the first argument through support_proposal
                    self.send_specific_message(mess, MessagePerformative.ARGUE)

            # COMMIT MESSAGE RECEIVED
            new_commit = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.COMMIT))
            )
            if new_commit:
                for mess in new_commit:
                    item = mess.get_content()
                    if (
                        self.get_item_from_name(item)
                        in self.get_preference_dict().keys()
                    ):
                        self.send_specific_message(mess, MessagePerformative.COMMIT)
                        # current agent received the item
                        self.remove_item(self.get_item_from_name(item))

            # ACCEPT MESSAGE RECEIVED
            new_accept = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.ACCEPT))
            )
            if new_accept:
                for mess in new_accept:
                    item = mess.get_content()
                    if (
                        self.get_item_from_name(item)
                        in self.get_preference_dict().keys()
                    ):
                        self.send_specific_message(mess, MessagePerformative.COMMIT)
                        # current agent sends the item
                        self.remove_item(self.get_item_from_name(item))

            # PROPOSE MESSAGE RECEIVED
            new_propose = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.PROPOSE))
            )
            if new_propose:
                for mess in new_propose:
                    # in protocol, curent agent accepts directly the proposed item if it is in the 10% preferred
                    is_in_10 = self.get_preference().is_item_among_top_10_percent(
                        mess.get_content(), list(self.get_preference_dict().keys())
                    )
                    if is_in_10:
                        self.send_specific_message(mess, MessagePerformative.ACCEPT)
                    else:
                        self.send_specific_message(mess, MessagePerformative.ASK_WHY)

        # NO MESSAGE RECEIVED: AGENT TRIES TO PROPOSE
        # check if the current agent has an item to propose
        elif len(self.get_item_list()) > 0:
            print("get_item_list : ",self.get_item_list)
            others = []
            for agent in self.get_model().get_agents():
                if agent != self:
                    others.append(agent)
            # in case of multiple other agents; other is an DiscussionAgent object
            other = random.choice(others)
            print("OTHER : ",other)
            print('get_name : ',self.get_name())
            print('get_pref : ',self.get_preference())
            proposition = self.get_preference().most_preferred(self.get_item_list())
            # proposition if an Item object
            message = Message(
                self.get_name(),
                other.get_name(),
                MessagePerformative.PROPOSE,
                proposition,
            )
            self.get_model().update_step()
            print(str(self.get_model().get_step()) + " : " + message.__str__())
            self.send_message(message)


    def remove_item(self, item):
        self.get_preference_dict().pop(item)
        self.get_preference().remove_item(item)

    def generate_preferences(self, List_items):
        pref = Preferences()
        pref.set_criterion_order_preference(List_items["crit_order"])
        List_items.pop("crit_order")
        for item in List_items:
            pref.set_criterion_name_list(List_items[item].keys())
            for criteria in List_items[item]:
                pref.add_criterion_value(
                    CriterionValue(item, criteria, List_items[item][criteria])
                )
        self.preference = pref


    def send_specific_message(
        self,
        message_received,
        performative,
        proposition=None,
        rebutal=False,
        premise=None,
    ):
        sender = message_received.get_exp()
        content = message_received.get_content()
        # BUILDS NEXT CONTENT
        if performative.__str__() == "PROPOSE":
            # check wether its in the middle of a session
            if proposition:
                new_content = proposition
        elif performative.__str__() == "ACCEPT":
            # if in the middle of a session, have to remove unecessary heads to retrieve the Item object
            if rebutal:
                # previous argument was an argument
                new_content = content.split(" <- ")[0]
                # previous argument was a counter-argument
                new_content = content.split(" , ")[0]
                # previous argument was a counter-argument
                if new_content[:4] == "not ":
                    new_content = new_content[4:]
            # directly accepts the Item (if in the 10% most preferred)
            else:
                new_content = content
        elif performative.__str__() == "ASK_WHY":
            new_content = content
        elif performative.__str__() == "COMMIT":
            new_content = content
        elif performative.__str__() == "ARGUE":
            # builds a counter-argument
            if rebutal and premise:
                # premise are the new arguments used
                new_content = premise
            # builds an argument with support_proposal function
            else:
                arg = self.support_proposal(content)
                if not arg:
                    performative = MessagePerformative.REFUSE
                    new_content = content
                else:
                    new_content = arg.__str__()
        # BUILDS NEXT MESSAGE, SENDS IT AND PRINTS IT
        message = Message(self.get_name(), sender, performative, new_content)
        self.send_message(message)
        self.get_model().update_step()
        print(str(self.get_model().get_step()) + " : " + message.__str__())

    def support_proposal(self, item):
        """
        Selects one Argument object to support the selectd Item object. Method called by the agent that
        proposes the item.
        input:
            item: Item object
        output:
            arg: Argument object (eg: "Diesel Engine <- ENVIRONMENT = BAD")
        """
        arg = Argument(False, item)
        proposals = arg.List_supporting_proposal(item, self.get_preference())
        if proposals:
            best_criteria = random.choice(
                [
                    argu
                    for argu in proposals
                    if self.get_preference().get_value(item, argu).value
                    == max(
                        [
                            self.get_preference().get_value(item, i).value
                            for i in proposals
                        ]
                    )
                ]
            )
            arg.add_premiss_couple_values(
                best_criteria, self.get_preference().get_value(item, best_criteria)
            )
            return arg
        else:
            return None

    def argument_parsing(self, argument_str):
        """
        input:
            argument_str: string data
        output:
            item: Item object
            premisces: string data
            rebutal: bool object
        """
        item = None
        if len(argument_str.split(" <- ")) > 1:
            # a new argument was given
            item_name, arguments = argument_str.split(" <- ")
            rebutal = False
        else:
            # its a counter argument
            item_name, arguments = argument_str.split(" , ")
            if item_name[:4] == "not ":
                item_name = item_name[4:]
            rebutal = True
        for i in self.get_item_list():
            if i.__str__() == item_name:
                item = i
                break
        premisces = arguments.split(", ")
        return [item, premisces, rebutal]

    def update_argument(self, item, premisces, other_agent_name, rebutal):
        """
        input :
            item : Item
            premisces : list of strings (with each string as Criterion.Name = Criterion.Value)
            other_agent_name : str
            rebutal : bool
        output :
            a list : [str of arguments, bool to update rebutal]
        """
        criteria = None
        value = None
        premisce = premisces[0]
        if len(premisce.split(" = ")) > 1:
            criteria, value = premisce.split(" = ")
            criteria, value = self.get_criteria_from_name(
                criteria
            ), self.get_value_from_name(value)
        elif len(premisce.split(" > ")) > 1:
            criteria, value = premisce.split(" > ")
            criteria, value = self.get_criteria_from_name(
                criteria
            ), self.get_criteria_from_name(value)
        if criteria == None:
            return [None, True]
        # The criterion is not important for him (regarding his order)
        # On suppose qu'il n'est pas important s'il est dans la seconde moitié des critères selon l'ordre de préférence de l'agent
        if (
            criteria
            in self.get_preference().get_criterion_order_preference()[
                -len(CriterionName) // 2 :
            ]
        ):
            # string: not item , criteria = value
            better_criteria = self.get_preference().get_criterion_order_preference()[0]
            string = "not " if not rebutal else ""
            string += (
                item.get_name()
                + " , "
                + better_criteria.__str__()
                + " > "
                + criteria.__str__()
            )
            return [string, False]
        # Its local value for the item is lower than the one of the other agent on the considered criteria
        # string: not item , criteria = value
        other_agent = self.get_model().agent_from_string(other_agent_name)
        if (
            self.get_preference().get_value(item, criteria).value
            < other_agent.get_preference().get_value(item, criteria).value
        ):
            string = "not " if not rebutal else ""
            string += (
                item.get_name()
                + " , "
                + criteria.__str__()
                + " = "
                + self.get_preference().get_value(item, criteria).__str__()
            )
            return [string, False]
        # He prefers another item and he can defend it by an argument with a better value on the same criterion.
        for new_item in self.get_item_list():
            if (
                self.get_preference().get_value(new_item, criteria).value
                > self.get_preference().get_value(item, criteria).value
            ):
                string = "not " if not rebutal else ""
                string += (
                    item.get_name()
                    + " , "
                    + new_item.get_name()
                    + " <- "
                    + criteria.__str__()
                    + " = "
                    + self.get_preference().get_value(new_item, criteria).__str__()
                )
                return [string, False]
        return [None, True]
        

class ArgumentModel (Model):
    
    def __init__(self, n_agent, preferences):
        super().__init__()
        # self.schedule = BaseScheduler(self)
        self.n_agent = n_agent
        self.preferences = preferences
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self.running = True
        self.current_step = 0
        
        # Initialize agents
        self.agents = self.initialize_agents()
        
    def initialize_agents(self):
        agents = []
        for idx in range(self.n_agent):
            agents.append(ArgumentAgent(idx, self, f"A{idx}", self.preferences[idx]))
            print(f"L'agent {agents[idx].get_name()} a été créé")
            self.schedule.add(agents[idx])
        
        return agents

    def get_step(self):
        return self.current_step

    def get_agents(self):
        return self.schedule.agents

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()

    def update_step(self):
        self.current_step += 1

    def agent_from_string(self, name):
        for agent in self.get_agents():
            if agent.get_name() == name:
                return agent
        return None
            
    


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
        },
        "crit_order": [
            CriterionName.PRODUCTION_COST,
            CriterionName.ENVIRONMENT_IMPACT,
            CriterionName.CONSUMPTION,
            CriterionName.DURABILITY,
            CriterionName.NOISE,
        ],
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
        },
        "crit_order": [
            CriterionName.ENVIRONMENT_IMPACT,
            CriterionName.NOISE,
            CriterionName.PRODUCTION_COST,
            CriterionName.CONSUMPTION,
            CriterionName.DURABILITY,
        ],
        }

    # Initialize the model
    argument_model = ArgumentModel(2, [agent_0_preferences, agent_1_preferences])

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
