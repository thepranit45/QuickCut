import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickcut.settings')
django.setup()

from bookings.models import Shop

def update_shop():
    shop = Shop.objects.first()
    if shop:
        shop.name = "24 K Hair Studio"
        shop.phone = "9209597436"
        shop.save()
        print(f"Updated shop to {shop.name} with phone {shop.phone}")
    else:
        print("No shop found.")

if __name__ == '__main__':
    update_shop()
