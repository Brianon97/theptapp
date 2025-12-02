# trainer/forms.py ← FINAL WORKING VERSION
from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['client_name', 'client_contact', 'date', 'time', 'notes', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Any notes...'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter client name'}),
            'client_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone or email'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get user if passed from view
        super().__init__(*args, **kwargs)

        self.fields['client_name'].label = "Client Name"
        self.fields['client_contact'].label = "Client Contact (Phone or Email)"
        self.fields['client_name'].required = True
        self.fields['client_contact'].required = False
        self.fields['notes'].required = False
        self.fields['date'].required = True
        self.fields['time'].required = True

        # Hide status from non-staff users
        if not user or not user.is_staff:
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['status'].initial = 'pending'
            self.fields['status'].required = False