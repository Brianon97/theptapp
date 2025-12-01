# trainer/views.py ← REPLACE YOUR ENTIRE FILE WITH THIS

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from .models import Booking
from .forms import BookingForm


@login_required
def booking_list(request):
    bookings = request.user.bookings.all().order_by('date', 'time')
    return render(request, 'booking_list.html', {'bookings': bookings})


@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, is_staff=request.user.is_staff)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.save()
            messages.success(request, 'Your booking has been created successfully!')
            return redirect('trainer:booking_list')
    else:
        form = BookingForm(is_staff=request.user.is_staff)

    return render(request, 'booking_form.html', {
        'form': form,
        'title': 'New Booking'
    })


@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking, is_staff=request.user.is_staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('trainer:booking_list')
    else:
        form = BookingForm(instance=booking, is_staff=request.user.is_staff)

    return render(request, 'booking_form.html', {
        'form': form,
        'title': 'Edit Booking',
        'booking': booking
    })


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('trainer:booking_list')

    return render(request, 'booking_confirm_delete.html', {'booking': booking})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('trainer:booking_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def check_notifications(request):
    if not request.user.is_staff:
        return JsonResponse({'count': 0})

    pending = Booking.objects.filter(status='pending').order_by('-created_at')
    count = pending.count()
    latest = pending.first()

    if latest:
        data = {
            'count': count,
            'latest': {
                'client_name': latest.client.get_full_name() or latest.client.username,
                'date': latest.date.strftime('%b %d'),
                'time': latest.time.strftime('%I:%M %p'),
                'status_display': latest.get_status_display()
            }
        }
    else:
        data = {'count': 0}

    return JsonResponse(data)