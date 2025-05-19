from django import forms
from .models import AttachmentApplication

class AttachmentApplicationForm(forms.ModelForm):
    class Meta:
        model = AttachmentApplication
        fields = '__all__'