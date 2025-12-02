# trainer/views.py
# MAJOR CHANGES:
# - Bookings now belong to trainer (not client)
# - Removed client=request.user checks
# - Updated notifications to show trainer's own pending bookings
# - Added is_staff=True on signup (so trainers get notification badge)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from .models import Booking
from .forms import BookingForm


# trainer/views.py
@login_required
def booking_list(request):
    if request.user.is_staff:
        # Trainer sees ALL bookings with client info
        bookings = Booking.objects.all().select_related('client').order_by('date', 'time')
    else:
        # Regular client only sees their own bookings
        bookings = request.user.bookings.all().order_by('date', 'time')

    return render(request, 'trainer/booking_list.html', {'bookings': bookings})


# trainer/views.py → replace these two functions

@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save()
            messages.success(request, 'Booking created successfully!')
            return redirect('trainer:booking_list')
    else:
        form = BookingForm(user=request.user)

    return render(request, 'trainer/booking_form.html', {
        'form': form,
        'title': 'New Booking'
    })

@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    # Only owner or staff can edit
    if not request.user.is_staff and booking.client != request.user:
        messages.error(request, "You can only edit your own bookings.")
        return redirect('trainer:booking_list')

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
    booking = get_object_or_404(Booking, pk=pk, trainer=request.user)
    if request.method == 'POST':
        client_name = booking.client_name
        booking.delete()
        messages.success(request, f'Booking for {client_name} cancelled.')
        return redirect('trainer:booking_list')
    return render(request, 'trainer/booking_confirm_delete.html', {'booking': booking})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True  # So they can see notifications + access admin
            user.save()
            login(request, user)
            messages.success(request, 'Welcome, Trainer! Your account is ready.')
            return redirect('trainer:booking_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def check_notifications(request):
    # Only show pending bookings for THIS trainer
    pending = Booking.objects.filter(trainer=request.user, status='pending').order_by('-created_at')
    count = pending.count()
    latest = pending.first()

    if latest:
        data = {
            'count': count,
            'latest': {
                'client_name': latest.client_name,
                'date': latest.date.strftime('%b %d'),
                'time': latest.time.strftime('%I:%M %p'),
            }
        }
    else:
        data = {'count': 0}

    return JsonResponse(data)