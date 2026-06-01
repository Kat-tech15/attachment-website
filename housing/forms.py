from django import forms
from .models import House, Booking

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['owner_name', 'phone_number', 'location', 'description', 'rent', 'total_rooms','image']

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