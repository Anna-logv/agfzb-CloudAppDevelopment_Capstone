import sys
from ibmcloudant.cloudant_v1 import Document, CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
#from ibm_cloud_sdk_core import ApiException
import requests

def main(param_dict):
    current_method=""
    if "__ow_method" in param_dict.keys():
        current_method=param_dict["__ow_method"].lower()

    if (not current_method in ['get','post']):
        return { 'statusCode':500, 'message': 'Something went wrong on the server' }

    try:
        authenticator = IAMAuthenticator(param_dict["IAM_API_KEY"])
        service = CloudantV1(authenticator=authenticator)
        service.set_service_url(param_dict["COUCH_URL"])
    except:
        return { 'statusCode':500, 'message': 'Something went wrong on the server' }
        
    #start get
    if (current_method=='get'):
        dealer_id=0
        entries=[]
        if ("dealerId" in param_dict.keys()):
            dealer_id_str=param_dict["dealerId"]
            if not dealer_id_str.isdigit():
                return { 'statusCode':404, 'message': 'dealerId does not exist' }
            dealer_id=int(dealer_id_str)
    
        if (dealer_id==0):
            response = service.post_all_docs(db='reviews', include_docs=True,limit=1000).get_result()  
            for row in response["rows"]:
                entries.append(row["doc"])
        else:
            response = service.post_find(
              db='reviews',
              selector={'dealership': dealer_id}
            ).get_result()
            for row in response["docs"]:
                entries.append(row)
            
        if len(entries)==0:
            return { 'statusCode':404, 'message': 'dealerId does not exist' }
        
        return {'result':entries}
    
    # start post    
    if (not "review" in param_dict.keys()):
        return { 'statusCode':500, 'message': 'Something went wrong on the server' }
        
    new_review=param_dict["review"]
    
    keys=["id","name","dealership","review","purchase","another","purchase_date","car_make","car_model","car_year"]   
    if not all(key in new_review for key in keys):
        return { 'statusCode':500, 'message': 'Something went wrong on the server' }
    
    try:
        response = service.get_document(db='reviews',doc_id=str(new_review["id"])).get_result()
        rev=str(response["_rev"])
    except:
        rev=""

    if rev=="":
        products_doc = Document(
            id = str(new_review["id"]),
            name = str(new_review["name"]),
            dealership = int(new_review["dealership"]),
            review = str(new_review["review"]),
            purchase = bool(new_review["purchase"]),
            another = str(new_review["another"]),
            purchase_date = str(new_review["purchase_date"]),
            car_make = str(new_review["car_make"]),
            car_model = str(new_review["car_model"]),
            car_year = int(new_review["car_year"])
            )
    else:
        products_doc = Document(
            id = str(new_review["id"]),
            name = str(new_review["name"]),
            dealership = int(new_review["dealership"]),
            review = str(new_review["review"]),
            purchase = bool(new_review["purchase"]),
            another = str(new_review["another"]),
            purchase_date = str(new_review["purchase_date"]),
            car_make = str(new_review["car_make"]),
            car_model = str(new_review["car_model"]),
            car_year = int(new_review["car_year"]),
            rev=str(rev)
            )   

    response = service.post_document(db='reviews', document=products_doc).get_result()

    return {'result':response}
