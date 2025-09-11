from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Attachee, Company, Tenant, Booking, House, Notification, Announcement

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check user type and create appropriate profile
        if instance.role == 'attachee':
            Attachee.objects.create(user=instance)
            print("Attachee profile created for:", instance.username)
        elif instance.role == 'company':
            Company.objects.create(user=instance)
            print("Company profile created for:", instance.username)
        elif instance.role == 'tenant':
            Tenant.objects.create(user=instance)
            print("Tenant profile created for:", instance.username)

@receiver(post_save, sender=Booking)
def booking_notifications(sender, instance, created, **kwargs):
    if created:
        # Notify landlord on new bookings'
        Notification.objects.create(
            recipient=instance.house.tenant,
            message=f"{instance.attachee.get_full_name()} boooked your house: {instance.house.title}",
            url=f"/house/{instance.house.id}/"

        )
    else:
        # notify attachee on booking approval
        if instance.status  == 'approved':
            Notification.objects.create(
                recipient=instance.attachee,
                message=f"Your booking for {instance.house.title} has been approved",
                url=f"/booking/{instance.id}/"
            )

@receiver(post_save, sender=House)
def house_posted_notifications(sender, instance, created, **kwargs):
    if created:
        # Notify all attachees of new house
        attachees = User.objects.filter(role='attachee')
        for attachee in attachees:
            Notification.objects.create(
                recipient=attachee,
                message=f"New house posted: {instance.title}",
                url=f"/house/{instance.id}/"
            )
    
@receiver(post_save, sender=Announcement)
def announcement_notifications(sender, instance, created, **kwargs):
    if created:
        # Notify all users about the announcement
        for user in users:
            Notification.objects.create(
                recipient=user,
                message=f"Admin Announcement: {instance.title}",
                url=f"/announcements/{instance.id}"
            )