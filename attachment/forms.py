from django import forms
from .models import AttachmentApplication, House, AttachmentPost, CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


user = get_user_model()

class AttachmentApplicationForm(forms.ModelForm):
    class Meta:
        model = AttachmentApplication
        fields = ['full_name', 'email', 'cv', 'cover_letter', 'recommendation']



class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [ 
        ('attachee', 'Attachee'),
        ('company', 'Company'),
        ('tenant', 'Tenant'),
        ('admin', 'Admin'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove the help text for all fields
        for field in self.fields:
            self.fields[field].help_text = None 


class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['owner_name', 'contact', 'location', 'description', 'rent','image']

class AttachmentPostForm(forms.ModelForm):
    class Meta:
        model = AttachmentPost
        fields = ['company', 'location', 'email', 'description', 'slots', 'application_deadline',]