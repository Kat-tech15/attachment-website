from django.db import models
from core import settings



class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='notifications'
        )
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notify_type = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"To {self.recipient.email}: {self.message[:20]}"
    
    class Meta:
        ordering = ['-created_at']

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    message = models.TextField()
    is_registered_user = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_identity = self.user.username if self.user else (self.name or "Anonymus")
        return f"Feedback by {user_identity} on {self.submitted_at.strftime('%Y-%m-%d')}"
    
class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Testimonials(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, blank=True)
    message = models.TextField()
    image = models.ImageField(upload_to='testimonials_photos/', default='default-avatar.jpg')

    def __str__(self):
        return f"{self.name} - {self.role}"