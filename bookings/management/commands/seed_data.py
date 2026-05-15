"""
Management command: python manage.py seed_data
Seeds the database with sample barbers, services, and time slots.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Service, Barber, TimeSlot, Shop
import datetime


SERVICES = [
    {'name': 'Classic Haircut', 'description': 'Traditional scissor cut with a clean finish.', 'duration_minutes': 30, 'price': 299, 'icon': 'cut'},
    {'name': 'Beard Trim & Shape', 'description': 'Expert beard sculpting for a sharp, groomed look.', 'duration_minutes': 20, 'price': 199, 'icon': 'spa'},
    {'name': 'Hair + Beard Combo', 'description': 'Full haircut plus beard trim in one session.', 'duration_minutes': 50, 'price': 449, 'icon': 'face'},
    {'name': 'Hot Towel Shave', 'description': 'Luxurious straight-razor shave with hot towel treatment.', 'duration_minutes': 40, 'price': 349, 'icon': 'water_drop'},
    {'name': 'Hair Color', 'description': 'Professional coloring with premium products.', 'duration_minutes': 90, 'price': 799, 'icon': 'palette'},
    {'name': 'Kids Haircut', 'description': 'Gentle and fun haircut for children under 12.', 'duration_minutes': 25, 'price': 199, 'icon': 'child_care'},
]

BARBERS = [
    {'name': 'Arjun Sharma', 'speciality': 'Fades & Modern Styles', 'bio': '8 years of craft, specializing in skin fades and contemporary men\'s styling.', 'rating': 4.9, 'experience_years': 8},
    {'name': 'Rahul Verma', 'speciality': 'Classic Cuts & Shaves', 'bio': 'Trained in traditional barbering with a passion for razor-sharp precision.', 'rating': 4.8, 'experience_years': 6},
    {'name': 'Dev Patel', 'speciality': 'Color & Creative Styles', 'bio': 'Expert colorist and creative stylist who loves pushing boundaries.', 'rating': 4.7, 'experience_years': 4},
]


def generate_slots(barber, days_ahead=14, start_hour=9, end_hour=20, interval=30):
    """Generate time slots for a barber for the next N days."""
    slots = []
    today = datetime.date.today()
    for day_offset in range(1, days_ahead + 1):
        date = today + datetime.timedelta(days=day_offset)
        # Skip Sundays (weekday() == 6)
        if date.weekday() == 6:
            continue
        current = datetime.time(start_hour, 0)
        end = datetime.time(end_hour, 0)
        while current < end:
            start_dt = datetime.datetime.combine(date, current)
            end_dt = start_dt + datetime.timedelta(minutes=interval)
            slot_end = end_dt.time()

            slots.append(TimeSlot(
                barber=barber,
                date=date,
                start_time=current,
                end_time=slot_end,
                is_booked=False,
            ))
            current = slot_end
    return slots


class Command(BaseCommand):
    help = 'Seed database with sample services, barbers, and time slots'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding QuickCut database...')

        TimeSlot.objects.all().delete()
        Appointment.objects.all().delete() if hasattr(self, '_') else None
        Barber.objects.all().delete()
        Shop.objects.all().delete()
        Service.objects.all().delete()

        # Seed Shop
        shop = Shop.objects.create(name='24 K Hair Sallon', address='Downtown Plaza', city='Mumbai', phone='9876543210')
        self.stdout.write(self.style.SUCCESS(f'  OK Created shop: {shop.name}'))

        # Seed Services
        for s in SERVICES:
            Service.objects.create(**s)
        self.stdout.write(self.style.SUCCESS(f'  OK Created {len(SERVICES)} services'))

        # Seed Barbers + Slots
        all_slots = []
        for b_data in BARBERS:
            barber = Barber.objects.create(shop=shop, **b_data)
            slots = generate_slots(barber)
            all_slots.extend(slots)
            self.stdout.write(self.style.SUCCESS(f'  OK Created barber: {barber.name} with {len(slots)} slots'))

        TimeSlot.objects.bulk_create(all_slots, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'  OK Bulk created {len(all_slots)} time slots'))
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))



