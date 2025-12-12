# trainer/admin.py
from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'client_name', 'client_contact', 'date', 'time',
        'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('client_name', 'client_contact', 'notes')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff:
            return qs
        return qs.none()  # optional: hide from non-staff