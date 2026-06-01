from django import forms
from .models import Notification, Feedback, Announcement

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