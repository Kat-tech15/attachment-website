from django import forms
from .models import AttachmentApplication, House, AttachmentPost
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
        model = user
        fields = ['username', 'email', 'role', 'password1', 'password2']

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['name', 'location', 'description', 'rent','image']

class AttachmentPostForm(forms.ModelForm):
    class Meta:
        model = AttachmentPost
        fields = ['company', 'location', 'email', 'description', 'slots', 'application_deadline',]