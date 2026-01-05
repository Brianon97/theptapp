# trainer/models.py
from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        null=True,
        blank=True
    )
    client = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='bookings_as_client',
        null=True,
        blank=True
    )
    client_name = models.CharField(max_length=100)
    client_contact = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending','Pending'),('confirmed','Confirmed'),('cancelled','Cancelled')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        trainer_name = self.trainer.get_full_name() or self.trainer.username if self.trainer else "Unassigned"
        client_str = self.client.get_full_name() or self.client.username if self.client else self.client_name
        return f"{client_str} → {trainer_name}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_created', 'New Booking'),
    ]
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    client_name = models.CharField(max_length=100, blank=True)
    booking_date = models.DateField(null=True, blank=True)
    booking_time = models.TimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username} - {self.created_at}"