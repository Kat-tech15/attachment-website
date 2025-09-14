from django import forms
from django.contrib.auth import authenticate
from .models import House, AttachmentPost, CustomUser, Booking, HouseReview, CompanyReview, Feedback
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from datetime import date

user = get_user_model()

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

class EmailLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *rgs, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = None
        super().__init__(*rgs, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if not email or not password:
            raise forms.ValidationError("Email and password are required.")
        
        self.user = authenticate(request=self.request, email=email, password=password)
        if self.user is None:
            raise forms.ValidationError("Invalid email or password.")
        
        if not user.email_verified:
            raise forms.ValidationError("Email not verified. Please check your email for the OTP.")
        
        if not self.user.is_active:
            raise forms.ValidationError("This account is inactive. Please verify your eamil to activate.")
            
        return cleaned_data
    
    def get_user(self):
        return self.user

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


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'placeholder':'Write your feedback here...',
                'rows': 2
            }),
            'name': forms.TextInput(attrs={'placeholder': 'Your name(optional)'}),
            'email': forms.TextInput(attrs={'placeholder': 'Your email(optional)'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['move_in_date', 'move_out_date']
        widgets = {
            'move_in_date': forms.DateInput(attrs={'type': 'date'}),
            'move_out_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['move_in_date'].initial = date.today()