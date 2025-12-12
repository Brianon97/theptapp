# trainer/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Booking


class BookingForm(forms.ModelForm):
    # This is the field that appears in the booking form
    client_contact = forms.CharField(
        max_length=20,
        required=False,
        label="Contact (Phone for SMS/reminders)",
        widget=forms.TextInput(attrs={
            'placeholder': '+1 555-123-4567',
            'autocomplete': 'tel',
            'inputmode': 'tel',
            'class': 'form-control',
        }),
        help_text="Optional – enter phone number for text reminders",
    )

    class Meta:
        model = Booking
        fields = ['client', 'date', 'time', 'status', 'notes', 'client_contact']
        
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Any special requests or notes...'
            }),
            # client_contact widget is defined above (not here) because it's a non-model field in some cases
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Only trainers can choose a client
        if user and user.is_staff:
            self.fields['client'].queryset = User.objects.filter(is_staff=False).order_by('first_name', 'last_name')
            self.fields['client'].empty_label = "— Select a client —"
            self.fields['client'].required = True
        else:
            # Clients can't pick who they book with — remove the field
            self.fields.pop('client', None)

        # When editing: pre-fill the contact field from saved data
        if self.instance.pk and self.instance.client_contact:
            self.fields['client_contact'].initial = self.instance.client_contact

        # Optional: hide status from clients (they shouldn't change it)
        if not (user and user.is_staff):
            self.fields.pop('status', None)