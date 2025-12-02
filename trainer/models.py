# trainer/models.py ← REPLACE THE WHOLE MODEL WITH THIS
from django.db import models

class Booking(models.Model):
    client_name = models.CharField(max_length=100)                    # ← New!
    client_contact = models.CharField(max_length=100, blank=True)      # ← New!
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
        return f"{self.client_name} – {self.date} {self.time}"