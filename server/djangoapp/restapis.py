import requests
import json
# import related models here
from .models import CarDealer,DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, ClassificationsOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if not "api_key" in kwargs:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        else:
            response =  requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'},
                                        auth=HTTPBasicAuth('apikey', kwargs["api_key"]))
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        if not "entries" in json_result:
            return results
        dealers = json_result["entries"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"], 
                city=dealer_doc["city"], 
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"], 
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                state=dealer_doc["state"],
                zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results
def analyze_review_sentiments(dealerreview):

# excited: Showing personal enthusiasm and interest
# frustrated: Feeling annoyed and irritable
# impolite: Being disrespectful and rude
# polite: Displaying rational, goal-oriented behavior
# sad: An unpleasant passive emotion
# satisfied: An affective response to perceived service quality
# sympathetic: An affective mode of understanding that involves emotional resonance

    watson_url="https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/efb40c20-765a-48ac-85b3-92eb30fc25f6"
    watson_api_key="qFQF2dmUdUVUl0dOh7PUpkK_wB8RncfejvEkT-a_6TDY"

    authenticator = IAMAuthenticator(watson_api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator)

    natural_language_understanding.set_service_url(watson_url)
    try:
        response = natural_language_understanding.analyze(
            text=dealerreview,
            features=Features(classifications=ClassificationsOptions(model='tone-classifications-en-v1'))).get_result()
    except:
        return "neutral"
    if not "classifications" in response:
        return "neutral"
    max_confidence=0
    tone=""
    for row in response["classifications"]:
        if float(row["confidence"])>max_confidence:
            max_confidence=row["confidence"]
            tone=str(row["class_name"])
    #print(json.dumps(response, indent=2))
    tones_positive=["excited","satisfied","sympathetic"]
    tones_negative=["frustrated","impolite","sad"]
    if tone in tones_positive:
        return "positive"
    if tone in tones_negative:
        return "negative"
    return "neutral"

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, **kwargs)
    if json_result:
        # Get the row list in JSON as dealers
        if not "result" in json_result:
            return results
        reviews = json_result["result"]
        # For each dealer object
        fields_array=['dealership', 'name', 'purchase', 'review', 'purchase_date', 'car_make', 'car_model', 'car_year', 'sentiment', 'id']
        for review in reviews:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            for field in fields_array:
                if not field in review:
                    review[field]=""
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment="",
                id=review["id"]
            )
            review_obj.sentiment=analyze_review_sentiments(review_obj.review)
            results.append(review_obj)

    return results
# def get_dealer_by_id_from_cf(url, dealerId):

# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_state_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,state=kwargs["state"])
    if json_result:
        # Get the row list in JSON as dealers
        if not "entries" in json_result:
            return results
        dealers = json_result["entries"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"], 
                city=dealer_doc["city"], 
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"], 
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                state=dealer_doc["state"],
                zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results
# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



