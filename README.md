# DONATION --- a django revamp of DONATE

DONATION is a web application that allows people to register bagged donations or search a map to pick up their neighbors contributions.  Written mainly in **Python** and **Javascript** and utilizing the **Django** framework, it connects users through a request system to fulfill bag pick ups and a locale finder powered by the [Google Maps API](https://developers.google.com/maps/documentation/javascript/tutorial).

------------
-----
## TABLE OF CONTENTS:

1. ### Files (notable)
2. ### Installation
3. ### Pages
4. ### Usage

------------
-----
### FILES:
- **db.sqlite3** - local dabatase which stores all users, bags, (bag) requests, and locations.
- **models.py** - contains data class structures and relations for mapping users to locations, bags, and requests.
- **views.py** - handles web app pages and their functions such creating new bags, finding bag locations, and creating/modifying requests successfully.
- **templates/donate** - html templates responsible for dynamically displaying page contents and requests from views.py. all populated bags, requests, and locations made possible with django templating. Important javascript responsible for making Google Maps API calls/events, AJAX requests for calling views.py functions, and other DOM modification is located in their respective templates.
- **static/donate/styles.css** - html styling elements for providing an easy-to-follow UI for user experience flow.

-------
------------

### INSTALLATION:
Requires [Python 3](https://www.python.org/downloads/), [Django](https://docs.djangoproject.com/en/2.2/topics/install/), and a popular web browser such as [Chrome](https://www.google.com/chrome/), [Firefox](https://www.mozilla.org/en-US/firefox/new/), or [Safari](https://www.apple.com/safari/).

#### Dependencies
* Open a Mac Terminal and run `pip install -r requirements.txt` after installing Python.
Package includes:
    * `django`
* Google API requires an API_KEY. A free one is provided in the source code.
    **Please refrain from abusing requests.**
------------
------

### USAGE:

#### Run Django application
In Terminal:
    1. `cd <directory where donate is located>`
    2. `python manage.py runserver`

#### Connect

* ##### **Register** (required)
    Users must create a unique username and provide an email upon registration.

* ##### **Login/Logout**
    Logging in is required in order to access all web app features.
**_First-time users will be met with a form to lookup and register their `location`_**.

#### Bags

* ##### **Add Bag**
    Put a bag of items up for donation. Specify the weight and applicable categories of its contents before submission. Multiple (or none) categories may be applied.

* ##### **Bag List**
    A list of all non-delivered user bags will display below showing its weight, categories, a unique bag # for tracking purposes, and pending request status if applicable.

* ##### **Requests**
    In addition to bag statistic may be a pending request status. Pending approvals will display A **&#10003;** and **&#10007**; button to allow immediate response. Approve requests will update and display **_pending delivery_** until delivery is complete.

#### Pick-up

* ##### **Locate/Markers**
    On load, the map will automatically center on your location. Interact with the map to find nearby markers (users). Clicking on a marker will display the user's username and populate a list of their bags available for request.
    **_Bags with a pending request will not populate on marker-click_**.

* ##### **Bag List**
    Bag statistics populated include weight, categories, and a `request` button if it is available. Click to send a request to the owner letting them know you are interested in picking it up!
    **_Only one request per bag may be active at any time until the owner approves or denies_**.


#### Requests

* ##### **Awaiting response: **&#10003;** and **&#10007;****
    Owners will see **&#10003;** and **&#10007;** to approve or deny an incoming request. Approval will mark the bag _pending delivery_, requiring pick up.

* ##### **Pending Approval**
    Requestors will see _pending approval_ as they wait for the owner to approve or deny the request.

* ##### **Pending Pickup**
    Owners will see _pending pickup_ to signify it is the requestor's duty to pick up and deliver your request-approved bag.
    **_Requestor contact info (email) will be revealed to you at this stage_**.

* ##### **Needs Your Delivery**
    Requestors will see _needs your delivery_ after their request is approved. Pressing the Complete to signify successful delivery, will delete the bag and its request.

#### Settings
 `Click on your username (upper right) to access settings`.

* ##### **Location**
    Displays your current saved location as well as form to update it.
    **_Location requires all fields be filled to comply with specificity requirement_**.

* ##### **Notifications**
    A hub for all notifications which displays bags requiring either your response or delivery. 
    **_An `alert` counter of your noficiations displays beside your username._**

* ##### **History/Pending**
    All bags of pending status where the current user is awaiting a response to a request, or a pending delivery or their bag will be shown here.
