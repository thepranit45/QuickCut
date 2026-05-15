from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Shop(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=30)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    icon = models.CharField(max_length=50, default='scissors')  # Font Awesome icon name

    def __str__(self):
        return self.name


class Barber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='barbers', null=True, blank=True)
    name = models.CharField(max_length=100)
    speciality = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='barbers/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    experience_years = models.IntegerField(default=1)
    is_manager = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['barber', 'date', 'start_time']

    def __str__(self):
        return f"{self.barber.name} - {self.date} {self.start_time}"

    @property
    def is_past(self):
        slot_dt = datetime.datetime.combine(self.date, self.start_time)
        slot_dt = timezone.make_aware(slot_dt)
        return slot_dt < timezone.now()


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=100)
    customer_email = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.customer_name} - {self.slot}"

    @property
    def total_price(self):
        return self.service.price
