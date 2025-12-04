# trainer/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Booking
from .forms import BookingForm
from django.db.models import Q
from django import forms
from django.contrib.auth.models import User



@login_required
def booking_list(request):
    if request.user.is_staff:
        bookings = request.user.bookings.all().order_by('-date', 'time')
    else:
        bookings = request.user.bookings_as_client.all().order_by('-date', 'time')
    return render(request, 'trainer/booking_list.html', {'bookings': bookings})

@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.is_staff:
                booking.trainer = request.user
                if form.cleaned_data.get('client'):
                    selected_client = form.cleaned_data['client']
                    booking.client = selected_client
                    booking.client_name = selected_client.get_full_name() or selected_client.username
                    booking.client_contact = selected_client.email or form.cleaned_data['client_contact']
            else:
                booking.client = request.user
                booking.trainer = form.cleaned_data['trainer']
            booking.save()
            messages.success(request, "Booking created!")
            return redirect('trainer:booking_list')
    else:
        form = BookingForm(user=request.user)
    return render(request, 'trainer/booking_form.html', {'form': form, 'title': 'New Booking'})

@login_required
def booking_edit(request, pk):
    # First get the booking (trainer OR client owns it)
    booking = get_object_or_404(Booking, Q(pk=pk) & (Q(trainer=request.user) | Q(client=request.user)))

    # Block clients from editing (for now)
    if not request.user.is_staff:
        messages.error(request, "Clients cannot edit bookings yet.")
        return redirect('trainer:booking_list')

    # Only trainers reach here
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated!')
            return redirect('trainer:booking_list')
    else:
        form = BookingForm(instance=booking, user=request.user)

    return render(request, 'trainer/booking_form.html', {
        'form': form,
        'title': 'Edit Booking',
        'booking': booking
    })

@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(
        Booking,
        Q(pk=pk) & (Q(trainer=request.user) | Q(client=request.user))
    )

    if request.method == 'POST':
        client_name = booking.client_name or "Client"
        booking.delete()
        messages.success(request, f'Booking for {client_name} cancelled.')
        return redirect('trainer:booking_list')

    return render(request, 'trainer/booking_confirm_delete.html', {'booking': booking})

def signup(request):
    # Trainer signup
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            login(request, user)
            messages.success(request, 'Welcome, Trainer! Your account is ready.')
            return redirect('trainer:booking_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})



class SignUpForm(UserCreationForm):
    ROLE_CHOICES = [
        ('client', 'I am a Client (booking sessions)'),
        ('trainer', 'I am a Trainer (receiving bookings)'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']

            if form.cleaned_data['role'] == 'trainer':
                user.is_staff = True
                welcome_msg = "Welcome, Trainer! You can now manage bookings."
            else:
                user.is_staff = False
                welcome_msg = "Welcome! You can now book sessions."

            user.save()
            login(request, user)
            messages.success(request, welcome_msg)
            return redirect('trainer:booking_list')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

@login_required
def check_notifications(request):
    if request.user.is_staff:
        pending = Booking.objects.filter(trainer=request.user, status='pending').order_by('-created_at')
    else:
        pending = Booking.objects.filter(client=request.user, status='pending').order_by('-created_at')
    count = pending.count()
    latest = pending.first()
    if latest:
        data = {
            'count': count,
            'latest': {
                'client_name': latest.client_name or "Someone",
                'date': latest.date.strftime('%b %d'),
                'time': latest.time.strftime('%I:%M %p'),
            }
        }
    else:
        data = {'count': 0}
    return JsonResponse(data)