# trainer/forms.py  ← FINAL WORKING VERSION – replace your entire file with this

from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'time', 'notes', 'status']   # correct – no service

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Any notes or special requests...'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Optional: hide status from clients when they create/edit
        is_staff = kwargs.pop('is_staff', False)
        super().__init__(*args, **kwargs)

        self.fields['notes'].required = False

        if not is_staff:
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['status'].initial = 'pending'