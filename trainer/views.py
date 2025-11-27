# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking
from .forms import BookingForm

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(client=request.user).order_by('date', 'time')
    return render(request, 'trainer/booking_list.html', {'bookings': bookings})

@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.save()
            messages.success(request, 'Booking created successfully!')
            return redirect('trainer:booking_list')
    else:
        form = BookingForm()
    return render(request, 'trainer/booking_form.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # THIS LINE IS THE FIX → change to where you want to go after login
            return redirect('home')          # or 'booking_list' or 'admin:index'
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login

def signup(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name.split()[0],
                last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
            )
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('trainer:booking_list')
    
    return render(request, 'signup.html')

# trainer/views.py  (add this function)
@login_required
def booking_edit(request, pk):
    booking = Booking.objects.get(pk=pk, client=request.user)  # security: only own bookings

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('trainer:booking_list')
    else:
        form = BookingForm(instance=booking)

    return render(request, 'trainer/booking_form.html', {
        'form': form,
        'booking': booking,
        'is_edit': True  # optional: to change title in template
    })
# trainer/views.py
from django.shortcuts import get_object_or_404

@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)  # only own booking
    
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('trainer:booking_list')
    
    return render(request, 'trainer/booking_confirm_delete.html', {'booking': booking})