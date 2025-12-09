# trainer/forms.py
from django import forms
from .models import Booking
from django.contrib.auth.models import User


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['client', 'date', 'time', 'status', 'notes', 'client_contact']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'client_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone or Email (optional if client selected)',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user and user.is_staff:
            # Trainer sees client dropdown
            clients_qs = User.objects.filter(is_staff=False).order_by('first_name', 'username')
            self.fields['client'].queryset = clients_qs
            self.fields['client'].empty_label = "-- Select existing client --"
            self.fields['client'].required = False  # Allow walk-ins

            # Add a "Walk-in / New Client" option
            self.fields['client'].choices = [('', '--- Or enter new client below ---')] + list(self.fields['client'].choices)

        # Make contact field optional
        self.fields['client_contact'].required = False
        self.fields['client_contact'].label = "Contact (phone/email)"

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        contact = cleaned_data.get('client_contact')

        # If no client selected, contact becomes required
        if not client and not contact:
            self.add_error('client_contact', "Please select a client OR enter contact info.")

        # Auto-fill client_name if client selected
        if client:
            cleaned_data['client_name'] = client.get_full_name() or client.username

        return cleaned_data

    def save(self, commit=True):
        booking = super().save(commit=False)
        if self.user.is_staff:
            booking.trainer = self.user

        # Use selected client if exists, otherwise use manual name/contact
        if not booking.client and self.cleaned_data.get('client_contact'):
            booking.client_name = "Walk-in Client"  # or let them type name too if you want

        if commit:
            booking.save()
        return booking