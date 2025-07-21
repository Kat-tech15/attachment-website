from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import  Attachee, Company, Contact, Tenant, CustomUser, ApplicationVisit,AttachmentPost, House,Testimonials,Feedback
# Register your models here.


admin.site.register(Company)
admin.site.register(Tenant)
admin.site.register(Contact)
admin.site.register(Attachee)
admin.site.register(ApplicationVisit)
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

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'is_registered_user', 'submitted_at')
    list_filter = ('is_registered_user',)
    search_fields = ('message', 'user__username', 'email', 'name')
    