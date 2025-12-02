# trainer/forms.py  ← REPLACE ENTIRE FILE
from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['client', 'client_contact', 'date', 'time', 'notes', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Any notes or special requests...'}),
            'client_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 083-1234567 or john@gmail.com'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # current user
        super().__init__(*args, **kwargs)

        # If regular client → hide client & contact, auto-fill
        if user and not user.is_staff:
            self.fields['client'].widget = forms.HiddenInput()
            self.fields['client'].initial = user
            self.fields['client_contact'].widget = forms.HiddenInput()
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['status'].initial = 'pending'
        else:
            # Trainer sees client dropdown
            self.fields['client'].queryset = User.objects.filter(is_staff=False)  # only real clients
            self.fields['client'].label = "Client Name"
            self.fields['client_contact'].label = "Client Contact (Phone or Email)"
            self.fields['client_contact'].help_text = "Optional – helpful for reminders"

        self.fields['notes'].required = False