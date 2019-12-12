from django.contrib import admin
from .models import BagCategory, Bag, Location, BagRequest

admin.site.register(BagCategory)
admin.site.register(Bag)
admin.site.register(Location)
admin.site.register(BagRequest)

# Register your models here.
