# trainer/views.py
# FINAL VERSION – works with client_name + client_contact text fields
# No more ForeignKey to User → no more .select_related('client') or request.user.bookings

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
    if request.user.is_staff:
        # Trainer sees ALL bookings
        bookings = Booking.objects.all().order_by('-date', 'time')
    else:
        # Regular user only sees bookings they made (by name)
        user_name = request.user.get_full_name() or request.user.username
        bookings = Booking.objects.filter(client_name__iexact=user_name).order_by('-date', 'time')

    return render(request, 'trainer/booking_list.html', {'bookings': bookings})


# trainer/views.py → booking_create (replace the whole function)
# trainer/views.py → booking_create (replace the whole function)
@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            # ← ONLY ONE success message
            messages.success(request, "Booking created successfully!")
            return redirect('trainer:booking_list')
        else:
            # Optional: show one error message if form invalid
            messages.error(request, "Please correct the errors below.")
    else:
        form = BookingForm(user=request.user)

    return render(request, 'trainer/booking_form.html', {
        'form': form,
        'title': 'New Booking'
    })


@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    # Only staff or person whose name matches can edit
    user_name = request.user.get_full_name() or request.user.username
    if not request.user.is_staff and booking.client_name.strip().lower() != user_name.strip().lower():
        messages.error(request, "You can only edit your own bookings.")
        return redirect('trainer:booking_list')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated!')
            return redirect('trainer:booking_list')
    else:
        form = BookingForm(instance=booking)

    return render(request, 'trainer/booking_form.html', {
        'form': form,
        'title': 'Edit Booking',
        'booking': booking
    })


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    user_name = request.user.get_full_name() or request.user.username
    if not request.user.is_staff and booking.client_name.strip().lower() != user_name.strip().lower():
        messages.error(request, "You can only delete your own bookings.")
        return redirect('trainer:booking_list')

    if request.method == 'POST':
        client_name = booking.client_name or "Client"
        booking.delete()
        messages.success(request, f'Booking for {client_name} cancelled.')
        return redirect('trainer:booking_list')

    return render(request, 'trainer/booking_confirm_delete.html', {'booking': booking})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True  # So trainers get full access
            user.save()
            login(request, user)
            messages.success(request, 'Welcome, Trainer! Your account is ready.')
            return redirect('trainer:booking_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def check_notifications(request):
    # Show pending bookings (all for staff, or by name for clients)
    if request.user.is_staff:
        pending = Booking.objects.filter(status='pending').order_by('-created_at')
    else:
        user_name = request.user.get_full_name() or request.user.username
        pending = Booking.objects.filter(
            client_name__iexact=user_name,
            status='pending'
        ).order_by('-created_at')

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