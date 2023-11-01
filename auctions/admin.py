from django.contrib import admin
from .models import *

class ListingAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlistedBy",)

# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(Category)