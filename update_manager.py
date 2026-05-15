import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickcut.settings')
django.setup()

from bookings.models import Barber, Service, Shop

def update_db():
    shop = Shop.objects.first()
    if not shop:
        print("No shop found!")
        return

    # Link services
    Service.objects.all().update(shop=shop)
    print("Linked all services to shop.")

    # Make Arjun a manager
    arjun = Barber.objects.filter(name__icontains="Arjun").first()
    if arjun:
        arjun.is_manager = True
        arjun.save()
        print(f"Made {arjun.name} the shop manager.")

if __name__ == '__main__':
    update_db()
