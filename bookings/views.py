from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
import datetime

from .models import Service, Barber, TimeSlot, Appointment, Shop
from .forms import AppointmentForm, BookingStep1Form, BookingStep2Form


# ─── Home / Landing ────────────────────────────────────────────────────────────

def home(request):
    services = Service.objects.all()
    barbers = Barber.objects.filter(is_active=True)
    shops = Shop.objects.filter(is_active=True)
    context = {
        'services': services,
        'barbers': barbers,
        'shops': shops,
    }
    return render(request, 'bookings/home.html', context)


# ─── Booking Flow ───────────────────────────────────────────────────────────────

def book(request):
    """Step 1 & 2: Service + Barber selection, then date selection."""
    services = Service.objects.all()
    barbers = Barber.objects.filter(is_active=True)
    shops = Shop.objects.filter(is_active=True)
    context = {
        'services': services,
        'barbers': barbers,
        'shops': shops,
    }
    return render(request, 'bookings/book.html', context)


def get_slots(request):
    """AJAX: return available time slots for a given barber + date."""
    barber_id = request.GET.get('barber_id')
    date_str = request.GET.get('date')

    if not barber_id or not date_str:
        return JsonResponse({'slots': [], 'error': 'Missing parameters'})

    try:
        date = datetime.date.fromisoformat(date_str)
        barber = Barber.objects.get(pk=barber_id, is_active=True)
    except (ValueError, Barber.DoesNotExist):
        return JsonResponse({'slots': [], 'error': 'Invalid barber or date'})

    slots = TimeSlot.objects.filter(
        barber=barber,
        date=date
    ).order_by('start_time')

    # Auto-generate slots if none exist for this day (and it's not a past day)
    if not slots.exists() and date >= timezone.localtime().date():
        current = datetime.time(9, 0)
        end = datetime.time(20, 0)
        new_slots = []
        while current < end:
            start_dt = datetime.datetime.combine(date, current)
            end_dt = start_dt + datetime.timedelta(minutes=30)
            new_slots.append(TimeSlot(
                barber=barber,
                date=date,
                start_time=current,
                end_time=end_dt.time()
            ))
            current = end_dt.time()
        TimeSlot.objects.bulk_create(new_slots)
        slots = TimeSlot.objects.filter(barber=barber, date=date).order_by('start_time')

    # Filter out past slots
    now = timezone.now()
    available = []
    for s in slots:
        slot_dt = datetime.datetime.combine(s.date, s.start_time)
        slot_dt = timezone.make_aware(slot_dt)
        if slot_dt > now:
            available.append({
                'id': s.id,
                'start': s.start_time.strftime('%I:%M %p'),
                'end': s.end_time.strftime('%I:%M %p'),
                'is_available': not s.is_booked,
            })

    return JsonResponse({'slots': available})


def confirm_booking(request):
    """POST: Final step — save the appointment."""
    if request.method != 'POST':
        return redirect('book')

    slot_id = request.POST.get('slot_id')
    service_id = request.POST.get('service_id')

    try:
        slot = TimeSlot.objects.get(pk=slot_id)
        if slot.is_booked:
            messages.error(request, 'Sorry, this time slot is no longer available! Please choose another.')
            return redirect('book')
    except (TimeSlot.DoesNotExist, ValueError):
        messages.error(request, 'Invalid time slot selected. Please try again.')
        return redirect('book')

    try:
        service = Service.objects.get(pk=service_id)
    except (Service.DoesNotExist, ValueError):
        messages.error(request, 'Invalid service selected. Please try again.')
        return redirect('book')

    form = AppointmentForm(request.POST)
    if form.is_valid():
        appointment = form.save(commit=False)
        appointment.barber = slot.barber
        appointment.service = service
        appointment.slot = slot
        appointment.status = 'confirmed'
        if request.user.is_authenticated:
            appointment.user = request.user
        appointment.save()

        # Mark slot as booked
        slot.is_booked = True
        slot.save()

        messages.success(request, 'Appointment confirmed! See you soon ✂️')
        return redirect('booking_success', pk=appointment.pk)
    else:
        # Re-render book page with errors
        services = Service.objects.all()
        barbers = Barber.objects.filter(is_active=True)
        shops = Shop.objects.filter(is_active=True)
        context = {
            'services': services,
            'barbers': barbers,
            'shops': shops,
            'form': form,
            'error': 'Please fix the errors below.',
        }
        messages.error(request, 'Please check your details and try again.')
        return redirect('book')


def booking_success(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'bookings/success.html', {'appointment': appointment})


# ─── My Appointments ────────────────────────────────────────────────────────────

def my_appointments(request):
    email = request.GET.get('email', '').strip()
    phone = request.GET.get('phone', '').strip()
    appointments = []
    searched = False

    if email or phone:
        searched = True
        qs = Appointment.objects.select_related('barber', 'service', 'slot')
        if email:
            qs = qs.filter(customer_email__iexact=email)
        if phone:
            qs = qs.filter(customer_phone=phone)
        appointments = qs.order_by('-created_at')

    return render(request, 'bookings/my_appointments.html', {
        'appointments': appointments,
        'searched': searched,
        'email': email,
        'phone': phone,
    })


def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        # Free the slot
        appointment.slot.is_booked = False
        appointment.slot.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('my_appointments')
    return render(request, 'bookings/cancel_confirm.html', {'appointment': appointment})


# ─── Services & Barbers ─────────────────────────────────────────────────────────

def services(request):
    all_services = Service.objects.all()
    return render(request, 'bookings/services.html', {'services': all_services})


def team(request):
    barbers = Barber.objects.filter(is_active=True)
    return render(request, 'bookings/team.html', {'barbers': barbers})


# ─── Barber Dashboard ──────────────────────────────────────────────────────────

@login_required
def barber_dashboard(request):
    try:
        barber = request.user.barber
    except Barber.DoesNotExist:
        messages.error(request, "You are not registered as a barber.")
        return redirect('home')

    today = timezone.localtime().date()
    
    if barber.is_manager and barber.shop:
        # Manager sees all shop appointments
        today_appointments = Appointment.objects.filter(
            barber__shop=barber.shop,
            slot__date=today
        ).select_related('slot', 'service', 'barber').order_by('slot__start_time')

        upcoming_appointments = Appointment.objects.filter(
            barber__shop=barber.shop,
            slot__date__gt=today,
            status='confirmed'
        ).select_related('slot', 'service', 'barber').order_by('slot__date', 'slot__start_time')
    else:
        # Regular barber sees only their own
        today_appointments = Appointment.objects.filter(
            barber=barber,
            slot__date=today
        ).select_related('slot', 'service').order_by('slot__start_time')

        upcoming_appointments = Appointment.objects.filter(
            barber=barber,
            slot__date__gt=today,
            status='confirmed'
        ).select_related('slot', 'service').order_by('slot__date', 'slot__start_time')

    context = {
        'barber': barber,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'today': today,
    }
    return render(request, 'bookings/barber_dashboard.html', context)


@login_required
def barber_action(request, pk, action):
    try:
        barber = request.user.barber
    except Barber.DoesNotExist:
        return redirect('home')

    if barber.is_manager and barber.shop:
        appointment = get_object_or_404(Appointment, pk=pk, barber__shop=barber.shop)
    else:
        appointment = get_object_or_404(Appointment, pk=pk, barber=barber)
    
    if action == 'complete':
        appointment.status = 'completed'
        appointment.save()
        messages.success(request, f"Appointment for {appointment.customer_name} marked as completed.")
    elif action == 'cancel':
        appointment.status = 'cancelled'
        appointment.save()
        appointment.slot.is_booked = False
        appointment.slot.save()
        messages.success(request, f"Appointment for {appointment.customer_name} cancelled.")

    return redirect('barber_dashboard')


@login_required
def shop_rates(request):
    try:
        barber = request.user.barber
        if not barber.is_manager or not barber.shop:
            messages.error(request, "Access denied. Managers only.")
            return redirect('barber_dashboard')
    except Barber.DoesNotExist:
        return redirect('home')

    services = Service.objects.filter(shop=barber.shop).order_by('name')

    if request.method == 'POST':
        for service in services:
            price_key = f'price_{service.id}'
            if price_key in request.POST:
                try:
                    new_price = float(request.POST[price_key])
                    service.price = new_price
                    service.save()
                except ValueError:
                    pass
        messages.success(request, "Service rates updated successfully.")
        return redirect('shop_rates')

    return render(request, 'bookings/shop_rates.html', {'services': services, 'barber': barber})


@login_required
def shop_slots(request):
    try:
        barber = request.user.barber
        if not barber.is_manager or not barber.shop:
            messages.error(request, "Access denied. Managers only.")
            return redirect('barber_dashboard')
    except Barber.DoesNotExist:
        return redirect('home')

    barbers = Barber.objects.filter(shop=barber.shop)
    
    selected_barber_id = request.GET.get('barber_id')
    selected_date_str = request.GET.get('date', timezone.localtime().date().isoformat())
    
    slots = []
    selected_barber = None

    try:
        selected_date = datetime.date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = timezone.localtime().date()

    if selected_barber_id:
        selected_barber = get_object_or_404(Barber, pk=selected_barber_id, shop=barber.shop)
        slots = TimeSlot.objects.filter(barber=selected_barber, date=selected_date).order_by('start_time')

        # Auto-generate slots if none exist for this day
        if not slots.exists() and selected_date >= timezone.localtime().date():
            current = datetime.time(9, 0)
            end = datetime.time(20, 0)
            new_slots = []
            while current < end:
                start_dt = datetime.datetime.combine(selected_date, current)
                end_dt = start_dt + datetime.timedelta(minutes=30)
                new_slots.append(TimeSlot(
                    barber=selected_barber,
                    date=selected_date,
                    start_time=current,
                    end_time=end_dt.time()
                ))
                current = end_dt.time()
            TimeSlot.objects.bulk_create(new_slots)
            slots = TimeSlot.objects.filter(barber=selected_barber, date=selected_date).order_by('start_time')

        # Check for appointments
        slot_data = []
        for slot in slots:
            apt = Appointment.objects.filter(slot=slot).first()
            slot_data.append({
                'slot': slot,
                'appointment': apt
            })
        slots = slot_data

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_block' and selected_barber:
            slot_id = request.POST.get('slot_id')
            slot = get_object_or_404(TimeSlot, pk=slot_id, barber=selected_barber)
            
            if not Appointment.objects.filter(slot=slot, status__in=['confirmed', 'pending']).exists():
                slot.is_booked = not slot.is_booked
                slot.save()
            else:
                messages.error(request, "Cannot block a slot that has an active appointment.")
                
            return redirect(f"{request.path}?barber_id={selected_barber_id}&date={selected_date_str}")

    context = {
        'barbers': barbers,
        'selected_barber': selected_barber,
        'selected_date': selected_date_str,
        'slots': slots,
        'barber': barber,
    }
    return render(request, 'bookings/shop_slots.html', context)
