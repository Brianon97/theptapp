# trainer/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Booking


def validate_irish_phone(value):
    """Validate Irish phone number format."""
    if not value:  # Allow empty since it's optional
        return
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-().]', '', value)
    
    # Irish phone patterns:
    # +353 followed by 9 digits (country code format)
    # 0 followed by 9 digits (local format)
    # 3 or 4 digits followed by variable length
    irish_patterns = [
        r'^\+353[0-9]{9}$',  # International format: +353 + 9 digits
        r'^0[0-9]{9}$',      # Local format: 0 + 9 digits
        r'^353[0-9]{9}$',    # Alternative international: 353 + 9 digits
    ]
    
    is_valid = any(re.match(pattern, cleaned) for pattern in irish_patterns)
    if not is_valid:
        raise ValidationError(
            'Please enter a valid Irish phone number. Examples: +353 1 234 5678 or 087 123 4567'
        )


class BookingForm(forms.ModelForm):
    # This is the field that appears in the booking form
    client_contact = forms.CharField(
        max_length=20,
        required=False,
        label="Contact (Phone for SMS/reminders)",
        validators=[validate_irish_phone],
        widget=forms.TextInput(attrs={
            'placeholder': '+353 87 123 4567',
            'autocomplete': 'tel',
            'inputmode': 'tel',
            'class': 'form-control',
        }),
        help_text="Optional – enter Irish phone number for text reminders (e.g., +353 87 123 4567 or 087 123 4567)",
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

    def save(self, commit=True):
        """Trim and persist contact number alongside default save."""
        instance = super().save(commit=False)
        instance.client_contact = self.cleaned_data.get('client_contact', '').strip()

        if commit:
            instance.save()
            self.save_m2m()

        return instance