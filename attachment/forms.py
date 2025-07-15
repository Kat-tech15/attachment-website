from django import forms
from .models import AttachmentApplication, House, AttachmentPost, CustomUser, HouseReview, CompanyReview
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


user = get_user_model()

class AttachmentApplicationForm(forms.ModelForm):
    class Meta:
        model = AttachmentApplication
        fields = ['attachment_post', 'attachee', 'status']



class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [ 
        ('attachee', 'Attachee'),
        ('company', 'Company'),
        ('tenant', 'Tenant'),
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
        fields = ['owner_name', 'phone_number', 'location', 'description', 'rent', 'total_rooms','image']

class AttachmentPostForm(forms.ModelForm):
    class Meta:
        model = AttachmentPost
        fields = ['location', 'email', 'description', 'slots', 'application_deadline', 'application_link',]
        widgets = {
            'application_deadline': forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and hasattr(self.user, 'company'):
           self.fields['email'].initial = self.user.company.email
           self.fields['location'].initial = self.user.company.location

class HouseReviewForm(forms.ModelForm):
    class Meta:
        model = HouseReview
        fields = ['rating', 'comment']


class CompanyReviewForm(forms.ModelForm):
    class Meta:
        model = CompanyReview
        fields = ['rating', 'comment']
    