from django.contrib import admin
from .models import CustomUser, Company, Attachee, Landlord, Contact


admin.site.register(CustomUser)
admin.site.register(Company)
admin.site.register(Landlord)
admin.site.register(Attachee)
admin.site.register(Contact)