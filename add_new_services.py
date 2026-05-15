import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickcut.settings')
django.setup()

from bookings.models import Service, Shop

def add_services():
    shop = Shop.objects.first()
    if not shop:
        print("No shop found!")
        return

    # Delete existing services
    Service.objects.all().delete()
    print("Deleted old services.")

    services_data = [
        {'name': 'Hair Cut', 'duration_minutes': 30, 'price': 299, 'icon': 'content_cut'},
        {'name': 'Hair Styling', 'duration_minutes': 30, 'price': 199, 'icon': 'auto_awesome'},
        {'name': 'Hair Colour', 'duration_minutes': 60, 'price': 499, 'icon': 'palette'},
        {'name': 'Hair Spa', 'duration_minutes': 45, 'price': 599, 'icon': 'spa'},
        {'name': 'Head Massage', 'duration_minutes': 30, 'price': 299, 'icon': 'self_improvement'},
        {'name': 'Hair Smoothing', 'duration_minutes': 120, 'price': 1499, 'icon': 'brush'},
        {'name': 'Keratin', 'duration_minutes': 120, 'price': 1999, 'icon': 'science'},
        {'name': 'Botox', 'duration_minutes': 120, 'price': 2499, 'icon': 'face'},
        {'name': 'Face Massage', 'duration_minutes': 30, 'price': 299, 'icon': 'self_improvement'},
        {'name': 'Facial', 'duration_minutes': 60, 'price': 799, 'icon': 'face_retouching_natural'},
        {'name': 'D-Tan', 'duration_minutes': 30, 'price': 399, 'icon': 'wb_sunny'},
        {'name': 'Clean-Up', 'duration_minutes': 30, 'price': 299, 'icon': 'cleaning_services'},
        {'name': 'Threading', 'duration_minutes': 15, 'price': 99, 'icon': 'gesture'},
        {'name': 'Waxing', 'duration_minutes': 30, 'price': 399, 'icon': 'sanitization'},
    ]

    for data in services_data:
        Service.objects.create(
            shop=shop,
            name=data['name'].upper(),
            duration_minutes=data['duration_minutes'],
            price=data['price'],
            icon=data['icon']
        )
        print(f"Added {data['name'].upper()}")

if __name__ == '__main__':
    add_services()
