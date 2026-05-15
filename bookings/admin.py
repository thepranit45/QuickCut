from django.contrib import admin
from django.utils.html import format_html
from .models import Service, Barber, TimeSlot, Appointment


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_minutes', 'price', 'icon')
    search_fields = ('name',)


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ('name', 'speciality', 'rating', 'experience_years', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'speciality')
    list_editable = ('is_active',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('barber', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('barber', 'date', 'is_booked')
    search_fields = ('barber__name',)
    list_editable = ('is_booked',)
    ordering = ('date', 'start_time')

    actions = ['mark_available']

    def mark_available(self, request, queryset):
        queryset.update(is_booked=False)
        self.message_user(request, "Selected slots marked as available.")
    mark_available.short_description = "Mark selected slots as available"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'customer_name', 'customer_phone', 'barber',
        'service', 'slot_display', 'status', 'colored_status', 'created_at'
    )
    list_filter = ('status', 'barber', 'service')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def slot_display(self, obj):
        return f"{obj.slot.date} at {obj.slot.start_time.strftime('%I:%M %p')}"
    slot_display.short_description = 'Appointment Slot'

    def colored_status(self, obj):
        colors = {
            'pending': '#f59e0b',
            'confirmed': '#10b981',
            'completed': '#6366f1',
            'cancelled': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span>', color
        )
    colored_status.short_description = ''
