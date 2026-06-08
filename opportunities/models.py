from django.db import models
from accounts.models import Attachee, Company
from django.utils import timezone

class AttachmentPost(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField()
    location = models.CharField(max_length=25)
    description = models.CharField(max_length=255)
    slots = models.IntegerField()
    application_link = models.URLField(help_text="Link to the application page.")
    application_deadline = models.DateField(null=True, blank=True)
    post_type = models.CharField(max_length=30, choices=[('attachment', 'Attachment'),('internship','Internship')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.post_type} ({self.application_deadline})"

class ApplicationVisit(models.Model):
    attachee = models.ForeignKey(Attachee, on_delete=models.CASCADE)
    attachment_post = models.ForeignKey(AttachmentPost, on_delete=models.CASCADE)
    visited_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('attachee', 'attachment_post')

    def __str__(self):
        return f"{self.attachee} visited {self.attachment_post}"