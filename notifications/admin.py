from django.contrib import admin
from .models import Announcement, Notification, Feedback, Testimonials

admin.site.register(Announcement)
admin.site.register(Notification)
admin.site.register(Feedback)
admin.site.register(Testimonials)