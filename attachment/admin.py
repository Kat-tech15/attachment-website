from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Attachee, Company, Contact, Tenant
# Register your models here.

admin.site.register(Company)
admin.site.register(Tenant)
admin.site.register(Contact)
admin.site.register(Attachee)

