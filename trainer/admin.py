# Register your models here.
from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('client__username', 'notes')