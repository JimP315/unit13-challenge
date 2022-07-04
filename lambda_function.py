### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta
#tday = datetime.date.today() #utilise today's date to ensure that date selected for meeting is in the future - this is giving an error 
#tdelta = datetime.timedelta(days=1) #allow participants to only select a meeting date at least 1 day from today 


### Functionality Helper Functions ###


def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")
#def parse_date(n): #do I need this and should then this be a str or what?  
    """
    #Securely converts a non-date value to date value.
    """
    #try: 
        #return date(n)
    #except ValueError: 
        #return float("nan")
        
def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

def validate_data(age, investment_amount, intent_request):  #meeting_date, ): - is this not working?
    """
    Validates the data provided by the user.
    """

    # Validate that the user's age is under 67 years old
    if age is not None:
        age = parse_int(age)
        if age > 67:
            return build_validation_result(
                False,
                "age",
                "You should be under the age of 67 to utilise  this service, "
                "please provide a different age, or please refer to our Retirement chat bot located here...provide link.",
            )
    if age is not None: 
        age = parse_int(age)
        if age < 18: #this to be more realistic since below zero makes no sense, just have it below 18 
            return build_validation_result(
                False,
                "age",
                "You should be at least 18 years old to utilise  this service, "
                "please provide a different age.",
            )


    # Validate the investment amount, it should be >= 5000
    if investment_amount is not None:
        investment_amount = parse_int(
            investment_amount
        )  # parameters are strings important to cast values
        if investment_amount < 5000:
            return build_validation_result(
                False,
                "investmentAmount",
                "The minimum investment amount must be at least $5,000 to use this service, "
                
                "please provide a suitable amount.",
            )
    # Validate the meeting date to be a weekday at least 1 day from today 
    #if meeting_date is not None:
        #meeting_date = parse_date(
           # meeting_date
        #)
        #if meeting_date < sum(tday + tdelta): #ensure that the date is at least 1 day from now or provide an error 
           #return build_validation_result(
                #False,
                #"meetingDate",
                #"The first meeting date available is from tomorrow,"
                
                #"please provide another suitable date.",
            #)
            
  # A True result will be returned if age or amount are valid - also need to code this for date 
    return build_validation_result(True, None, None)
    


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    #meeting_date = get_slots(intent_request)["meetingDate"]
    risk_levels = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.

        slots = get_slots(intent_request)
        validation_result = validate_data(age, investment_amount, intent_request)
        

        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None
            
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )


        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))
        
    initial_recommendation = get_investment_recommendation(risk_levels)
    
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} we'll discuss further when we catch up, and note this isn't personalised advice:
            With your risk preference, my suggestion is a portfolio with {}
            """.format(
                first_name, initial_recommendation
            #"contentType": "PlainText",
            #"content": """{} thanks for your time today, someone will be in touch within the next 48 hours to get you started
            #""" - What I want to do here is have a sign off after the investment recommendation 
            ),
        },
    )

def get_investment_recommendation(risk_level):
    """
    Returns an initial investment recommendation based on the risk profile.
    """
    
    if risk_level == "None":
        initial_recommendation = "100% Defensive (Bonds, etc), 0% Growth (Shares, Property, etc)"
    elif risk_level == "Very Low":
        initial_recommendation = "70% Defensive (Bonds, etc), 30% Growth (Shares, Property, etc)"
    elif risk_level == "Low":
        initial_recommendation = "50% Defensive (Bonds, etc), 50% Growth (Shares, Property, etc)"
    elif risk_level == "Medium":
        initial_recommendation = "30% Defensive (Bonds, etc), 70% Growth (Shares, Property, etc)"
    elif risk_level == "High":
        initial_recommendation = "10% Defensive (Bonds, etc), 90% Growth (Shares, Property, etc)"
    else: 
        initial_recommendation = "0% Defensive (Bonds, etc), 100% Growth (Shares, Property, etc)"
    
    return initial_recommendation


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
