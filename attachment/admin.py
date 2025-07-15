from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import  Attachee, Company, Contact, Tenant, CustomUser, AttachmentApplication,AttachmentPost, House,Testimonials
# Register your models here.


admin.site.register(Company)
admin.site.register(Tenant)
admin.site.register(Contact)
admin.site.register(Attachee)
admin.site.register(AttachmentApplication)
admin.site.register(AttachmentPost)
admin.site.register(House)
admin.site.register(Testimonials)

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ( 
        ('Role Info', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'location')
    search_fields = ['user']