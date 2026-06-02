from django.contrib import admin
from .models import CustomUser, Company, Attachee, Tenant, Contact


admin.site.register(CustomUser)
admin.site.register(Company)
admin.site.register(Tenant)
admin.site.register(Attachee)
admin.site.register(Contact)