# trainer/views.py
from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from .models import Booking, Notification
from .forms import BookingForm


@login_required
def booking_list(request):
    if request.user.is_staff:
        bookings = request.user.bookings.all().order_by('-date', 'time')
    else:
        bookings = request.user.bookings_as_client.all().order_by(
            '-date', 'time')
    return render(request, 'trainer/booking_list.html',
                  {'bookings': bookings})


@login_required
def booking_create(request):
    if not request.user.is_staff:
        messages.error(request, "Only trainers can create bookings.")
        return redirect('trainer:booking_list')

    if request.method == 'POST':
        # 🔥 CLEAR ANY EXISTING SUCCESS MESSAGES TO PREVENT DUPLICATES
        storage = messages.get_messages(request)
        list(storage)  # forces clearing

        form = BookingForm(request.POST, user=request.user)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.trainer = request.user
            booking.client = form.cleaned_data['client']
            booking.client_name = booking.client.get_full_name() or booking.client.username
            booking.client_contact = form.cleaned_data.get('client_contact', '').strip()

            booking.save()

            messages.success(request, f"Booking created for {booking.client_name}!")
            return redirect('trainer:booking_list')

    else:
        form = BookingForm(user=request.user)

    return render(request, 'trainer/booking_form.html', {
        'form': form,
        'title': 'New Booking'
    })

@login_required
def booking_edit(request, pk):
    # Get the booking (trainer OR client owns it)
    booking = get_object_or_404(
        Booking, Q(pk=pk) & (
            Q(trainer=request.user) | Q(client=request.user)))

    # Block clients from editing (for now)
    if not request.user.is_staff:
        messages.error(request, "Clients cannot edit bookings yet.")
        return redirect('trainer:booking_list')

    # Only trainers reach here
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking, user=request.user)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.client_contact = form.cleaned_data.get('client_contact', '').strip()
            updated.save()
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
        trainer = booking.trainer
        
        # If a client is cancelling, notify the trainer
        if not request.user.is_staff and trainer:
            Notification.objects.create(
                recipient=trainer,
                notification_type='booking_cancelled',
                message=f"{client_name} has cancelled their booking",
                client_name=client_name,
                booking_date=booking.date,
                booking_time=booking.time
            )
        
        booking.delete()
        messages.success(request, f'Booking for {client_name} cancelled.')
        return redirect('trainer:booking_list')

    return render(request, 'trainer/booking_confirm_delete.html', {'booking': booking})


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
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.email = form.cleaned_data.get('email', '')

            role = form.cleaned_data['role']
            if role == 'trainer':
                user.is_staff = True
                welcome_msg = "Welcome, Trainer! You can now manage bookings with your clients."
            else:
                user.is_staff = False
                welcome_msg = "Welcome! You can now view sessions with trainers."

            user.save()
            login(request, user)

            # This message will trigger a beautiful 3-second toast
            messages.success(request, welcome_msg)

            return redirect('trainer:booking_list')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def check_notifications(request):
    if request.user.is_staff:
        # Get unread notifications count for trainers
        unread_notifications = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        
        # Get pending bookings count
        pending_bookings = Booking.objects.filter(
            trainer=request.user, 
            status='pending'
        ).count()
        
        # Total notification count
        total_count = unread_notifications + pending_bookings
        
        # Get latest notification
        latest_notification = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).first()
        
        if latest_notification:
            data = {
                'count': total_count,
                'latest': {
                    'client_name': latest_notification.client_name,
                    'date': latest_notification.booking_date.strftime('%b %d') if latest_notification.booking_date else '',
                    'time': latest_notification.booking_time.strftime('%I:%M %p') if latest_notification.booking_time else '',
                    'type': latest_notification.notification_type,
                }
            }
        else:
            # Fall back to pending bookings if no notifications
            pending = Booking.objects.filter(trainer=request.user, status='pending').order_by('-created_at').first()
            if pending:
                data = {
                    'count': total_count,
                    'latest': {
                        'client_name': pending.client_name or "Someone",
                        'date': pending.date.strftime('%b %d'),
                        'time': pending.time.strftime('%I:%M %p'),
                        'type': 'booking_pending',
                    }
                }
            else:
                data = {'count': 0}
    else:
        # For clients, just show pending bookings
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


@login_required
def client_detail(request, user_id):
    if not request.user.is_staff:
        msg = "You don't have permission to view client profiles."
        messages.error(request, msg)
        return redirect('trainer:booking_list')

    # Clients only
    client = get_object_or_404(User, id=user_id, is_staff=False)
    bookings = client.bookings_as_client.all().order_by('-date', 'time')

    return render(request, 'trainer/client_detail.html', {
        'client': client,
        'bookings': bookings,
    })


@login_required
def notifications_list(request):
    """Display all notifications for trainers"""
    if not request.user.is_staff:
        messages.error(request, "Only trainers can view notifications.")
        return redirect('trainer:booking_list')
    
    # Get all notifications for this trainer
    notifications = Notification.objects.filter(recipient=request.user)
    
    # Mark all as read
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'trainer/notifications.html', {
        'notifications': notifications
    })


class CustomLoginView(SuccessMessageMixin, LoginView):
    template_name = 'login.html'
    success_message = "Welcome back! You are now logged in."

    def get_success_url(self):
        return reverse_lazy('trainer:booking_list')


class CustomLogoutView(LogoutView):
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            name = (request.user.get_short_name() or
                    request.user.username)
            msg = f"See you soon, {name}! You've been logged out."
            messages.success(request, msg)
        return super().dispatch(request, *args, **kwargs)




