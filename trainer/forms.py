# trainer/forms.py  ← Replace the whole file with this

from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'time', 'service', 'notes', 'status']  # ← removed duplicate 'time'
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only make truly optional fields optional
        self.fields['notes'].required = False
        # date, time, service stay required (Django default)
        # status is required for trainer edits, but if you want clients to not see it:
        # self.fields['status'].widget = forms.HiddenInput()