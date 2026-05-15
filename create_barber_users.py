import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickcut.settings')
django.setup()

from django.contrib.auth.models import User
from bookings.models import Barber

def setup_users():
    for barber in Barber.objects.all():
        username = barber.name.lower().replace(" ", "")
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password('barber123')
            user.save()
            print(f"Created user {username} for {barber.name}")
        else:
            print(f"User {username} already exists")
        
        barber.user = user
        barber.save()
        print(f"Linked user {username} to {barber.name}")

if __name__ == '__main__':
    setup_users()
