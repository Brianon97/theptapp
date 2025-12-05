# trainer/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Booking

# trainer/forms.py
from django import forms
from .models import Booking
from django.contrib.auth.models import User


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'time', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_staff:
            # Trainer: Add client dropdown + hide status from create form
            self.fields['client'] = forms.ModelChoiceField(
                queryset=User.objects.filter(is_staff=False).order_by('first_name', 'last_name'),
                label="Select Client",
                empty_label="— Choose a client —",
                widget=forms.Select(attrs={'class': 'form-select'}),
                required=True
            )

            # Optional: hide status on create (trainer confirms later)
            if not self.instance.pk:  # Only on create
                self.fields.pop('status', None)

        else:
            # Client booking themselves? (Future feature) — hide client fields
            pass  # Not implemented yet