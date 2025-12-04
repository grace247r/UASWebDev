from django.contrib import admin
from .models import Booking


class BookingAdmin(admin.ModelAdmin):
    list_display = ('passenger_name', 'origin', 'destination', 'airline', 'price', 'created_at')
    list_filter = ('airline', 'created_at')

admin.site.register(Booking, BookingAdmin)