# trainer/forms.py
from django import forms
from .models import Booking
from django.contrib.auth.models import User

# trainer/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Booking

class BookingForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=False),
        empty_label="— Select a client —",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Booking
        fields = ['client', 'date', 'time', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_staff:
            self.fields['client'].queryset = User.objects.filter(is_staff=False).order_by('first_name', 'username')
    class Meta:
        model = Booking
        fields = ['date', 'time', 'notes', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_staff:
            # Trainer → show dropdown of real clients
            self.fields['client'] = forms.ModelChoiceField(
                queryset=User.objects.filter(is_staff=False).order_by('first_name', 'last_name'),
                widget=forms.Select(attrs={'class': 'form-control'}),
                label="Select Client",
                empty_label="Choose a client..."
            )
            # Hide status from form (trainer can change later)
            if 'status' in self.fields:
                del self.fields['status']

        else:
            # Client booking themselves → hide everything
            self.fields['client_name'].widget = forms.HiddenInput()
            self.fields['client_contact'].widget = forms.HiddenInput()