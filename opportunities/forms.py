from django import forms
from .models import AttachmentPost

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