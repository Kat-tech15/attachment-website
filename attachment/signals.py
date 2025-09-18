from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Attachee, Company, Tenant, Booking, House, Notification, Announcement, AttachmentPost

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
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
def booking_status_notification(sender, instance, created, **kwargs):
    if not created:
        if instance.status == 'approaved':
            Notification.objects.create(
                recipient=instance.attachee,
                message = f"Your booking for {instance.house_post} has been approved."
            )
        elif instance.status == 'cancelled':
            Notification.objects.create(
                recipient=instance.attachee,
                message = f"Your booking for {instance.house_post} has been cancelled."
            ) 

@receiver(post_save, sender=Booking)
def notify_tenant_on_booking(sender, instance, created, **kwargs):
    if created:
        Notification.object.create(
            user=instance.house.tenant,
            message=f"{instance.attachee.username} booked your house: {instance.house.title}"
        )

@receiver(post_save, sender=AttachmentPost)
def notify_attachees_on_new_post(sender, instance, created, **kwargs):
    if created:
        attachees = User.objects.filter(role="attachee")
        for user in attachees:
            Notification.objects.create(
                user = user,
                message=f"New attachment posted by {instance.company.name}: {instance.title}"
            )