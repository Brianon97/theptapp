# trainer/forms.py ← REPLACE ENTIRE FILE
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
        super().__init__(*args, **kwargs)
        # Everyone sees the same simple form
        self.fields['client_name'].required = True
        self.fields['client_contact'].required = False
        self.fields['notes'].required = False
        
        # Optional: hide status from regular users
        if not kwargs.get('instance') and not getattr(kwargs.get('request'), 'user', None):
            pass  # keep status visible
        # Or hide it completely if you want:
        # self.fields['status'].widget = forms.HiddenInput()