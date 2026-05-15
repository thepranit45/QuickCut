from django import forms
from .models import Appointment, Service, Barber, TimeSlot
import datetime


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['customer_name', 'customer_email', 'customer_phone', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your full name',
                'id': 'id_customer_name',
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your@email.com',
                'id': 'id_customer_email',
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+91 98765 43210',
                'id': 'id_customer_phone',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Any special requests or notes...',
                'rows': 3,
                'id': 'id_notes',
            }),
        }
        labels = {
            'customer_name': 'Full Name',
            'customer_email': 'Email Address',
            'customer_phone': 'Phone Number',
            'notes': 'Special Requests',
        }


class BookingStep1Form(forms.Form):
    """Step 1: Choose Service and Barber"""
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_service'}),
        label='Select Service',
        empty_label='-- Choose a Service --',
    )
    barber = forms.ModelChoiceField(
        queryset=Barber.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_barber'}),
        label='Select Barber',
        empty_label='-- Choose a Barber --',
    )


class BookingStep2Form(forms.Form):
    """Step 2: Choose Date"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'id': 'id_date',
            'min': datetime.date.today().isoformat(),
        }),
        label='Select Date',
    )
