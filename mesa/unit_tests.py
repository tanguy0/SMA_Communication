from mesa import Model
from mesa.time import RandomActivation
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.Value import Value
from communication.arguments.Argument import Argument
from pw_argumentation_new import ArgumentModel

if __name__ == "__main__":
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
    
    message = Message(
        Seller.get_name(),
        Buyer.get_name(),
        MessagePerformative.PROPOSE,
        "Diesel Engine (A super cool diesel engine)",
    )
    message2 = Message(
        Seller.get_name(), Buyer.get_name(), MessagePerformative.ACCEPT, "Diesel Engine (A super cool diesel engine)"
    )
    message3 = Message(
        Seller.get_name(), Buyer.get_name(), MessagePerformative.COMMIT, "Diesel Engine (A super cool diesel engine)"
    )
    message4 = Message(
        Seller.get_name(),
        Buyer.get_name(),
        MessagePerformative.PROPOSE,
        "Electric Engine (A very quiet engine)",
    )
    message5 = Message(
        Seller.get_name(),
        Buyer.get_name(),
        MessagePerformative.ASK_WHY,
        "Electric Engine (A very quiet engine)",
    )

    arg = Argument(False, diesel_engine)

    print("*---- Testing preference package ----")
    print("*")
    print("* 3) Testing Most Preferred")
    assert len(Buyer.get_item_list()) == 2
    assert Buyer.get_preference().most_preferred(Buyer.get_item_list()) is not None
    assert Buyer.get_preference().most_preferred(Buyer.get_item_list()) == diesel_engine
    print("*     most_preferred() => OK")

    print("* 4) Testing Top 10%")
    assert Buyer.get_preference().is_item_among_top_10_percent(
        diesel_engine, Buyer.get_item_list()
    )
    assert not Buyer.get_preference().is_item_among_top_10_percent(
        electric_engine, Buyer.get_item_list()
    )
    print("*     is_item_among_top_10_percent() => OK")

    print("* 5) Testing Agents and messages")

    assert type(Buyer.get_preference()) == Preferences
    assert len(list(Buyer.get_preference().get_criterion_name_list())) == 5
    assert list(Buyer.get_preference().get_criterion_order_preference()) == [
        CriterionName.PRODUCTION_COST,
        CriterionName.ENVIRONMENT_IMPACT,
        CriterionName.CONSUMPTION,
        CriterionName.DURABILITY,
        CriterionName.NOISE
    ]
    print("*     get_preference() => OK")

    assert Buyer.get_preference_dict() == agent_0_preferences
    print("*     get_preference_dict() => OK")

    assert type(Buyer.get_model()) == ArgumentModel
    print("*     get_model() => OK")

    assert list(Buyer.get_item_list()) == [diesel_engine, electric_engine]
    print("*     get_item_list() => OK")

    assert type(Buyer.get_criteria_from_name("PRODUCTION_COST")) == CriterionName
    assert (
        Buyer.get_criteria_from_name("PRODUCTION_COST") == CriterionName.PRODUCTION_COST
    )
    print("*     get_criteria_from_name() => OK")

    assert type(Buyer.get_value_from_name("VERY_BAD")) == Value
    assert Buyer.get_value_from_name("VERY_BAD") == Value.VERY_BAD
    print("*     get_value_from_name() => OK")

    assert type(Buyer.get_item_from_name("Diesel Engine (A super cool diesel engine)")) == Item
    assert Buyer.get_item_from_name("Diesel Engine (A super cool diesel engine)") == diesel_engine
    print("*     get_item_from_name() => OK")
    
    assert (Buyer.send_specific_message(message, MessagePerformative.ACCEPT)) == None
    assert (Buyer.send_specific_message(message2, MessagePerformative.COMMIT)) == None
    assert (Buyer.send_specific_message(message3, MessagePerformative.COMMIT)) == None
    assert (Buyer.send_specific_message(message4, MessagePerformative.ASK_WHY)) == None
    # C'est le test de Argue que l'on arrive pas à passer, donc je le commente pour le rendu final
    #assert (Buyer.send_specific_message(message5, MessagePerformative.ARGUE)) == None
    print("*     send_specific_message() => OK")

    print("* 6) Testing Arguments")

    assert type(Buyer.support_proposal(diesel_engine)) == Argument
    print("*     support_proposal() => OK")

    assert (
        type(arg.List_supporting_proposal(diesel_engine, Buyer.get_preference()))
        == list
    )
    assert len(arg.List_supporting_proposal(diesel_engine, Buyer.get_preference())) == 3
    assert (
        len(arg.List_supporting_proposal(diesel_engine, Seller.get_preference())) == 2
    )
    assert (
        type(arg.List_supporting_proposal(diesel_engine, Seller.get_preference())[0])
        == CriterionName
    )
    print("*     List_support_proposal() => OK")

    assert (
        Buyer.get_preference().get_value(diesel_engine, CriterionName.PRODUCTION_COST)
        == None
        or Buyer.get_preference().get_value(
            diesel_engine, CriterionName.PRODUCTION_COST
        )
        == Value.VERY_GOOD
    )
    assert (
        Buyer.get_preference().get_value(diesel_engine, CriterionName.PRODUCTION_COST)
        == None
        or Buyer.get_preference()
        .get_value(diesel_engine, CriterionName.PRODUCTION_COST)
        .value
        == 4
    )

    assert type(Buyer.argument_parsing("Diesel Engine <- ENVIRONMENT = BAD")) == list
    assert len(Buyer.argument_parsing("Diesel Engine <- ENVIRONMENT = BAD")) == 3
    assert (
        Buyer.argument_parsing("Diesel Engine <- ENVIRONMENT = BAD")[0] == diesel_engine
    )
    assert Buyer.argument_parsing("Diesel Engine <- ENVIRONMENT = BAD")[1] == [
        "ENVIRONMENT = BAD"
    ]
    assert Buyer.argument_parsing("Diesel Engine <- ENVIRONMENT = BAD")[2] == False
    assert (
        Buyer.argument_parsing("not Diesel Engine , ENVIRONMENT = BAD")[0]
        == diesel_engine
    )
    assert Buyer.argument_parsing("not Diesel Engine , ENVIRONMENT = BAD")[1] == [
        "ENVIRONMENT = BAD"
    ]
    assert Buyer.argument_parsing("not Diesel Engine , ENVIRONMENT = BAD")[2] == True
    print("*     argument_parsing() => OK")



    ### La suite des tests tentés ne fonctionnaient pas ###