from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_by_state_from_cf, get_dealer_reviews_from_cf,post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import uuid

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
     return render(request, 'djangoapp/about.html')
# ...


# Create a `contact` view to return a static contact page
def contact(request):
     return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            messages.success(request,'You are logged in')
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            messages.error(request, 'Error: try again later')
            return redirect('djangoapp:index')
    else:
        messages.error(request,'Error: try again later')
        return redirect('djangoapp:index')
# ...

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')
# ...

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)
# ...

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships_old(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/index.html', context)


def get_dealerships(request):
    if request.method == "GET":
        context={}
        #url = "your-cloud-function-domain/dealerships/dealer-get"
        url="https://eu-gb.functions.appdomain.cloud/api/v1/web/803af88f-d896-4246-b09f-45e37f258fa9/api/dealership.json"
        # Get dealers from the URL
        # dealerships = get_dealers_from_cf(url)
        if "state" in request.GET:
            dealerships = get_dealer_by_state_from_cf(url,state=request.GET["state"])
        else:
            dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        context["dealership_list"]=dealerships
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context={}
        context["dealer_name"]=""

        url="https://eu-gb.functions.appdomain.cloud/api/v1/web/803af88f-d896-4246-b09f-45e37f258fa9/api/dealership.json"
        dealerships = get_dealers_from_cf(url)
        for dealer in dealerships:
            if int(dealer.id)==int(dealer_id):
               context["dealer_name"]=dealer.full_name

        url="https://eu-gb.functions.appdomain.cloud/api/v1/web/803af88f-d896-4246-b09f-45e37f258fa9/api/review.json"
        reviews = get_dealer_reviews_from_cf(url,dealerId=dealer_id)
        context["reviews_list"]=reviews
        context["dealer_id"]=dealer_id
        #reviews_names = ' | '.join([review.name+" ["+str(review.sentiment)+"] "+str(review.review) for review in reviews])
        #return HttpResponse(reviews_names)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if not request.user.is_authenticated:
        messages.error(request,'Error: you need to login first')
        return redirect('djangoapp:index')
# {
# "review": 
#     {
#         "id": "11142",
#         "name": "Upkar Lidder",
#         "dealership": 15,
#         "review": "Great service!",
#         "purchase": false,
#         "another": "field",
#         "purchase_date": "02/16/2021",
#         "car_make": "Audi",
#         "car_model": "Car",
#         "car_year": 2021
#     }
# }
    context={}
    context["dealer_id"]=dealer_id
    if request.method == "POST":
        url="https://eu-gb.functions.appdomain.cloud/api/v1/web/803af88f-d896-4246-b09f-45e37f258fa9/api/review.json"
        current_user=request.user.username
        if request.user.first_name!='' or request.user.last_name!='':
            current_user=request.user.first_name+" "+request.user.last_name
        data = request.POST

        purchasecheck = data.get("purchasecheck")=='on'
        content = data.get("content")
        car=data.get("car")
        purchasedate=data.get("purchasedate")
        car_model=CarModel.objects.get(pk=car)
        review = dict()
        review["id"] = uuid.uuid4().hex
        review["name"] = current_user
        review["dealership"] = dealer_id
        review["review"] = content
        review["purchase"] = purchasecheck
        review["purchase_date"] = purchasedate
        review["car_make"] = car_model.carmake.name
        review["car_model"] = car_model.name
        review["car_year"] = car_model.year.strftime("%Y")

        json_payload=dict()
        json_payload["review"] = review
        result=post_request(url, json_payload)
        print(json_payload)
        if not "result" in result:
            messages.error(request,'Error: unable to save review. Try again later')
            return redirect('djangoapp:index')
        if not "ok" in result["result"]:
            messages.error(request,'Error: unable to save review. Try again later')
            return redirect('djangoapp:index')
        messages.success(request,'Thank you! Your review has been saved')
        return redirect('djangoapp:dealer_details', dealer_id)
        return HttpResponse(str(result))
    
    url="https://eu-gb.functions.appdomain.cloud/api/v1/web/803af88f-d896-4246-b09f-45e37f258fa9/api/dealership.json"
    dealerships = get_dealers_from_cf(url)
    for dealer in dealerships:
        if int(dealer.id)==int(dealer_id):
            context["dealer_name"]=dealer.full_name

    context["cars"]=CarModel.objects.filter(dealer_id=dealer_id)
    return render(request, 'djangoapp/add_review.html', context)