# trainer/views.py  ← Replace the whole file with this

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Booking
from .forms import BookingForm


# ──────────────────────────────────────────────
# Client views (regular logged-in users)
# ──────────────────────────────────────────────
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


@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)

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
        'is_edit': True
    })


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)

    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('trainer:booking_list')

    return render(request, 'trainer/booking_confirm_delete.html', {'booking': booking})


# ──────────────────────────────────────────────
# Auth views
# ──────────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('trainer:booking_list')   # or 'home' or wherever you want
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')


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


# ────────────────────────────────────────────────
# Trainer notifications (on-screen bell/toast)
# ──────────────────────────────────────────────
def check_notifications(request):
    # Only authenticated users
    if not request.user.is_authenticated:
        return JsonResponse({"count": 0})

    # Allow: any staff member OR your personal email(s)
    allowed_emails = ["brianon1997@gmail.com"]  # ← add more trainers here later
    if not (request.user.is_staff or request.user.email in allowed_emails):
        return JsonResponse({"count": 0})

    # Look for bookings changed in the last 5 minutes
    recent = Booking.objects.filter(
        updated_at__gte=timezone.now() - timedelta(minutes=5)
    ).order_by('-updated_at')

    count = recent.count()
    latest = recent.first()

    if latest:
        latest_data = {
            "client_name": latest.client_name or latest.client.get_full_name(),
            "date": latest.date.strftime("%b %d"),
            "time": latest.time.strftime("%I:%M %p"),
            "status_display": latest.get_status_display(),
        }
    else:
        latest_data = None

    return JsonResponse({
        "count": count,
        "latest": latest_data
    })