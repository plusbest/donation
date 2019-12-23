from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError

from .models import Location, BagCategory, Bag, BagRequest
from .forms import LocationForm

import os
import requests
import json

# Create your views here.

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def index(request):
    ''' Home page for main actions'''

    # Require logged session
    if request.user.id is None:
        return render(request, "donate/login.html")

    # Check for user location
    try:
        my_location = Location.objects.get(user__id=request.user.id)

    # Force user to location page if none
    except Location.DoesNotExist:
        return HttpResponseRedirect(reverse("location"))

    return render(request, "donate/index.html")


def login_user(request):
    ''' Login and authentication for users '''

    if request.method == "POST":

        # Store submitted credentials
        username = request.POST["username"]
        password = request.POST["password"]

        # Store login info as user
        user = authenticate(request, username=username, password=password)

        # Verify user input
        if user is not None:

            # Django function to verify user
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

        # Reload page with error on failed login
        else:
            return render(request, "donate/login.html", {"message": "Invalid credentials"})

    return render(request, "donate/login.html")


def logout_user(request):
    ''' Logs out current user '''

    # Django logout func
    logout(request)

    return render(request, "donate/login.html", {"message": "Logged out"})


def register_user(request):
    ''' Registration handling for new users '''

    if request.method == "POST":

        # Store submitted registration info
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        passconfirm = request.POST["passconfirm"]

        # Check for password match
        if password != passconfirm:
            return render(request, "donate/register.html", {"message": "Passwords do not match"})

        else:
            # Verify input
            if username is not None:

                # Attempt new user registration by creating object
                try:
                    User.objects.create_user(
                        username=username, email=email, password=password)
                    return render(request, "donate/login.html", {"message": "Successfully registered."})

                # Error handle failed registration parameters
                except IntegrityError:
                    return render(request, "donate/register.html", {"message": "Username already taken"})

    return render(request, "donate/register.html")


def locate(request):
    ''' Search form for verified location via google maps API profile update '''


    # Query existing user location
    try:
        mylocation = Location.objects.get(user__id=request.user.id)

    # Create location object for user if none found
    except Location.DoesNotExist:
        mylocation = Location(user=request.user)
        mylocation.save()

    if request.method == 'POST':

        # Initialize google api-friendly address list
        google_address = []

        # Iterate Location model fields
        for field in Location._meta.get_fields():

            # Assign input value to matching field name if found
            if request.POST.get(field.name):

                google_address.append(request.POST.get(field.name))

                # Update Location field with input value
                setattr(mylocation, str(field.name),
                        request.POST.get(field.name))

        '''Counts elements to ensure address is specific enough six fields are
            required by user to have a proper pick up location for their bags'''
        if len(google_address) < 6:

            return HttpResponseRedirect(reverse("location"))

        else:

            # Retrieve Lat and Lon from API call JSON response
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={google_address}&key={GOOGLE_API_KEY}"

            # Get API request data
            r = requests.get(url)

            # JSON format response
            json_response = r.json()

            # Obtain coordinates from API response
            coord = json_response['results'][0]['geometry']['location']

            # Set Location object with new coords
            mylocation.lat = coord['lat']
            mylocation.lng = coord['lng']

            # Save location
            mylocation.save()

        return HttpResponseRedirect(reverse("index"))

    context = {
        "MyAddress": mylocation
    }

    return render(request, "donate/location.html", context)


def new_bag(request):
    ''' Adds new bag for logged user '''

    if request.method == 'POST':

        # Obtain bag weight
        weight = request.POST.get('weight')

        # Obtain categories list
        categories = request.POST.getlist('categorylist[]')

        # Create new bag object
        newbag = Bag(user=request.user, lbs=weight)

        # Save bag
        newbag.save()

        # Add selected categories to saved bag
        for category_id in categories:

            # Query category object
            category_add = BagCategory.objects.get(id=int(category_id))
            newbag.category.add(category_add)

    context = {
        "BagCategory": BagCategory.objects.all(),
        "MyBags": Bag.objects.filter(user__id=request.user.id),
    }

    return render(request, "donate/bag.html", context)


def discovery(request):
    ''' Find bags nearby to pickup '''

    # Initialize coords variables
    coords_dict = {}
    coords_list = []

    # Query logged user
    logged_user = User.objects.get(id=request.user.id)

    # Get logged user coords
    my_lat = logged_user.locale.lat
    my_lng = logged_user.locale.lng

    # API call for nearby Salvation Army locations
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={my_lat},{my_lng}&radius=5000&name=Salvation+Army&key={GOOGLE_API_KEY}"
    print(f"********** URL:  {url}")
    # Get API request data
    r = requests.get(url)

    # JSON format response
    json_response_nearby = r.json()

    # Store all nearby results
    candidate_coords = json_response_nearby['results']

    print("***** START -- CANDIDATE JSON RESPONSE *****")
    print(candidate_coords)
    print("***** END -- CANDIDATE JSON RESPONSE *****")

    # Adds candidate (Salvation Army) to coords dict list
    for candidate in candidate_coords:

        # Donation store's google place ID
        place_id = candidate['place_id']

        # API call for candidate store details
        url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,formatted_phone_number,geometry,opening_hours&key={GOOGLE_API_KEY}"

        r = requests.get(url)

        # JSON format response
        json_response_placeinfo = r.json()

        # Store hours of operation
        store_hours = json_response_placeinfo['result']['opening_hours']['weekday_text']
        store_name = json_response_placeinfo['result']['name']

        coords_dict['lat'] = float(candidate['geometry']['location']['lat'])
        coords_dict['lng'] = float(candidate['geometry']['location']['lng'])
        coords_dict['candidate'] = "True"
        coords_dict['place_id'] = candidate['place_id']
        coords_dict['place_name'] = candidate['name']
        coords_dict['hours'] = json_response_placeinfo['result']['opening_hours']['weekday_text']

        # Add dict to coords list
        coords_list.append(dict(coords_dict))

    # Iterate all user locations and store coordinates in dict list
    for location in Location.objects.all():

        # Store dict key value pairs to coords dict
        coords_dict['userid'] = location.user.id
        coords_dict['lat'] = float(location.lat)
        coords_dict['lng'] = float(location.lng)
        coords_dict['candidate'] = "False"

        # Add dict to coords list
        coords_list.append(dict(coords_dict))

    context = {
        "MyAddress": Location.objects.get(user__id=request.user.id),
        "NearbyCoords": coords_list,
        "NearbyCoordsJSON": json.dumps(coords_list),  # Note json.dumps()
    }

    return render(request, "donate/discover.html", context)


def user_settings(request):
    ''' Settings page with location change and bag/pickup overview for logged user '''

    form = LocationForm()

    # Bags with requests
    myreqbags = Bag.objects.filter(user=request.user, request__isnull=False)

    # Requests sent
    myrequests_to = BagRequest.objects.filter(requestor=request.user)

    # Requests received
    myrequests_from = BagRequest.objects.filter(owner=request.user)

    # Query existing user location
    try:
        mylocation = Location.objects.get(user__id=request.user.id)

    # Create location object for user if none found
    except Location.DoesNotExist:
        mylocation = Location(user=request.user)
        mylocation.save()

    context = {
        "MyRequestsTo": myrequests_to,
        "MyRequestsFrom": myrequests_from,
        "MyRequestBags": myreqbags,
        "MyAddress": mylocation,
        "form": form,
    }

    return render(request, "donate/settings.html", context)


def ajax_bagload(request):
    ''' AJAX request to return bags of user at clicked map marker'''

    # Get requested user
    userid = request.GET.get('userid', None)

    # Query all available (no request pending) bags of clicked user
    bagtemp = Bag.objects.filter(user__id=int(userid), request__isnull=True)

    '''Serialize queryset for JSON using 'natural key = True'
        allows for ManyToMany field to return string instead of id.'''
    bagdump = serializers.serialize(
        'python', bagtemp, use_natural_foreign_keys=True)

    # Format serialized data for JSON
    bagjson = json.dumps(bagdump, cls=DjangoJSONEncoder)

    data = {
        "Bags": bagjson,
    }

    return JsonResponse(data)


def ajax_bagrequest(request):
    ''' AJAX request to return bags of user at clicked map marker'''

    # Get requested bag id
    bagid = request.GET.get('bagid', None)

    # Query bag object
    bag = Bag.objects.get(id=bagid)

    # Query user (requestor) object
    requestor_user = request.user

    # Ensure user is not requesting their own bag
    if request.user.id == bag.user.id:

        message = "You can't request your own bags..."

        data = {
            "message": message,
        }

        return JsonResponse(data)

    else:

        # Check for existing request
        if bag.request:

            # Disallow and return error message
            message = "Bag already requested and pending owner approval."

            data = {
                "message": message,
            }
            return JsonResponse(data)

        else:

            # Create and save new request
            new_req = BagRequest(owner=bag.user, requestor=requestor_user)
            new_req.save()

            # Append request to bag and save
            bag.request = (new_req)
            bag.save()

            # Return success message
            message = "Bag succesfully requested!"

        data = {
            "message": message,
            "success": "success",
        }

        return JsonResponse(data)


def ajax_donationspot(request):
    ''' AJAX request to return bags of user at clicked map marker'''

    # Get donation place id
    place_id = request.GET.get('place_id', None)
    print(place_id)

    # API CALL
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,formatted_phone_number,geometry,opening_hours&key={GOOGLE_API_KEY}"

    message = "placeholder message"

    r = requests.get(url)

    # JSON format response
    json_response = r.json()

    # Store hours of operation
    store_hours = json_response['result']['opening_hours']['weekday_text']
    store_name = json_response['result']['name']

    data = {
        "message": "test message",
        "name": store_name,
        "hours": store_hours,
    }

    return JsonResponse(data)


def ajax_modrequest(request):
    ''' AJAX request handles modification actions to pending requests'''

    # Store requested action type
    mod_type = request.GET.get('mod_type', None)

    # Store Request ID
    req_id = request.GET.get('req_id', None)

    # Query Request object
    req = BagRequest.objects.get(id=int(req_id))

    # Update Request status on approval
    if mod_type == "approve":

        # Set approved status
        req.approved = True
        req.save()
        message = "Approval sent :)"

    # Delete Request on deny
    elif mod_type == "deny":

        # Find requests bag
        bag = req.bag_req

        # Set bag request to None
        bag.request = None
        bag.save()

        # Delete Request
        req.delete()

        message = "Request deny has been sent :("

    # Delete request on cancel
    elif mod_type == "cancel":

        # Find bag related to Request
        bag = req.bag_req

        '''Request must first be removed from bag before
            it can be itself deleted'''
        bag.request = None
        bag.save()

        # Delete request
        req.delete()

        message = "Request cancel successful :/"

    # Delete request and bag on completed pickup
    elif mod_type == "complete":

        # Find requests bag
        bag = req.bag_req

        '''Request must first be removed from bag before
            it can be itself deleted'''
        bag.request = None
        bag.save()

        # Delete Request
        req.delete()

        # Delete bag on donate completion
        bag.delete()

        message = "Delivery completion sent :D"

    # Necessary?
    else:
        pass

    data = {
        "message": message,
        "url": reverse("bag"),
    }

    return JsonResponse(data)


def ajax_notifications(request):
    ''' AJAX request to check for how many action items
        pending (aka notifications)'''

    alerts = (BagRequest.objects.filter(owner=request.user, approved=False) |
              BagRequest.objects.filter(requestor=request.user, approved=True)).count()

    data = {
        "alerts": alerts,
    }

    return JsonResponse(data)


def test_form(request):

    print(f"request data {request.POST}")

    form = LocationForm()

    # Query existing user location
    try:
        mylocation = Location.objects.get(user__id=request.user.id)

    # Create location object for user if none found
    except Location.DoesNotExist:
        mylocation = Location(user=request.user)
        mylocation.save()

    if request.method == 'POST':

        # Gets curated current page URL
        thisurl = request.POST.get('thisurl')[1:]

        # Initialize google api-friendly address list
        google_address = []

        # Bind request data to form
        form = LocationForm(request.POST)

        if form.is_valid():

            # Iterate Location model fields
            for field in Location._meta.get_fields():

                # Assign input value to matching field name if found
                if request.POST.get(field.name):

                    # Append field value to google address list
                    google_address.append(request.POST.get(field.name))

                    # Update Location field with input value
                    setattr(mylocation, str(field.name),
                            request.POST.get(field.name))

            # Retrieve Lat and Lng from API call JSON response
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={google_address}&key={GOOGLE_API_KEY}"

            # Get API request data
            r = requests.get(url)

            # JSON format response
            json_response = r.json()

            # Obtain coordinates from API response
            coord = json_response['results'][0]['geometry']['location']

            # Set Location object with new coords
            mylocation.lat = coord['lat']
            mylocation.lng = coord['lng']

            # Save location object changes
            mylocation.save()

            context = {
                "message": "successful form!",
                "form": form,
                "MyLocation": mylocation
            }
            return render(request, f"donate/{thisurl}.html", context)

        else:

            context = {
                "message": "unsuccessful form",
                "form": form,
                "MyLocation": mylocation
            }
            return render(request, f"donate/{thisurl}.html", context)
            # request.build_absolute_uri(reverse('view_name', args=(obj.pk, )))

    context = {
        "form": form,
        "MyLocation": mylocation,
    }

    return render(request, "donate/testform.html", context)







