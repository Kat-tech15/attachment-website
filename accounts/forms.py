from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from accounts.models import CustomUser
from notifications.models import Feedback



class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [ 
        ('attachee', 'Attachee'),
        ('company', 'Company'),
        ('landlord', 'Landlord'),
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
        
        if not self.user.email_verified:
            raise forms.ValidationError("Email not verified. Please check your email for the OTP.")
        
        if not self.user.is_active:
            raise forms.ValidationError("This account is inactive. Please verify your eamil to activate.")
            
        return cleaned_data
    
    def get_user(self):
        return self.user

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