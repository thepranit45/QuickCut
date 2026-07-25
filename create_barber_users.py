import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickcut.settings')
django.setup()

from django.contrib.auth.models import User
from bookings.models import Barber, Shop

def setup_users():
    # 1. Main 'barber' account
    user, created = User.objects.get_or_create(username='barber')
    user.set_password('barber123')
    user.is_staff = True
    user.save()
    
    shop = Shop.objects.first()
    barber, _ = Barber.objects.get_or_create(user=user, defaults={
        'name': 'Barber Manager',
        'shop': shop,
        'is_manager': True,
        'rating': 5.0,
        'experience_years': 5
    })
    barber.is_manager = True
    barber.save()
    print("Main user 'barber' created with password 'barber123'.")

    # 2. Existing barbers
    for b in Barber.objects.all():
        if b.user:
            continue
        username = b.name.lower().replace(" ", "")
        u, created = User.objects.get_or_create(username=username)
        if created:
            u.set_password('barber123')
            u.save()
        b.user = u
        b.save()
        print(f"Linked user {username} to barber {b.name}")

if __name__ == '__main__':
    setup_users()
