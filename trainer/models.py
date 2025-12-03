# trainer/models.py
from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        null=True,      # ← ADD THIS
        blank=True      # ← AND THIS
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

    def __str__(self):
        return f"{self.client_name} → {self.trainer.get_full_name() or self.trainer.username}"