from django.conf import settings
from django.db import models

# Create your models here.


class BagCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def natural_key(self):
        return (self.name)

    def __str__(self):
        return (self.name)


class BagRequest(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, related_name="owner_request")
    requestor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  default=None, null=True, blank=True, related_name="user_request")
    approved = models.BooleanField(default=False)

    def natural_key(self):
        return f"owner:{self.owner}, requestor:{self.requestor}, approved:{self.approved}"

    def __str__(self):
        return f"(owner:{self.owner}) - (requestor:{self.requestor}) - approved:{self.approved}"


class Location(models.Model):

    # Field names follows google maps API component names
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="locale")
    street_number = models.IntegerField(null=True, blank=True)
    route = models.CharField(max_length=128, null=True, blank=True)
    locality = models.CharField(max_length=64, null=True, blank=True)
    administrative_area_level_1 = models.CharField(
        max_length=2, null=True, blank=True)
    country = models.CharField(max_length=64, null=True, blank=True)
    postal_code = models.IntegerField(null=True, blank=True)

    # Lat and Lng for google maps markers
    lat = models.DecimalField(max_digits=16, decimal_places=12, default=0.0)
    lng = models.DecimalField(max_digits=16, decimal_places=12, default=0.0)

    def __str__(self):
        return f"({self.user})- {self.street_number} - {self.route} - {self.locality} - {self.administrative_area_level_1} - {self.postal_code}"


class Bag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="bags")
    lbs = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    category = models.ManyToManyField(BagCategory, related_name="bags")
    request = models.OneToOneField(
        BagRequest, on_delete=models.PROTECT, null=True, blank=True, default=None, related_name="bag_req")
    # desc = Charfield()
    # img = ????

    def __str__(self):
        return f"({self.user}) - {self.lbs} - {self.category} - request: {self.request}"
