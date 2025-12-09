# trainer/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


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

    def __str__(self):
        trainer_name = self.trainer.get_full_name() or self.trainer.username if self.trainer else "Unassigned"
        client_str = self.client.get_full_name() or self.client.username if self.client else self.client_name
        return f"{client_str} → {trainer_name}"
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='trainer_profile'
    )
    bio = models.TextField(max_length=800, blank=True)
    photo = models.ImageField(upload_to='trainers/', blank=True, null=True)
    specialties = models.CharField(
        max_length=300,
        blank=True,
        help_text="e.g. Strength Training, Weight Loss, Yoga, Mobility"
    )
    years_experience = models.PositiveIntegerField(default=1)
    qualifications = models.TextField(
        blank=True,
        help_text="Certifications, degrees, awards..."
    )
    instagram = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Hide inactive trainers

    class Meta:
        verbose_name = "Trainer Profile"
        verbose_name_plural = "Trainer Profiles"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} – Trainer"