from django import forms
from .models import Application
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class AttachmentApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'


user = get_user_model()

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