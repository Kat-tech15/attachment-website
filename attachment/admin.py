from django.contrib import admin
from .models import AttacheeInfo, AttacheeFirmInfo, ContactInfo, TenantsInfo
# Register your models here.

admin.site.register( AttacheeFirmInfo)
admin.site.register( TenantsInfo)
admin.site.register( ContactInfo )
admin.site.register(AttacheeInfo )