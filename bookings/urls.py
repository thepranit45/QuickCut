from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book, name='book'),
    path('book/slots/', views.get_slots, name='get_slots'),
    path('book/confirm/', views.confirm_booking, name='confirm_booking'),
    path('book/success/<int:pk>/', views.booking_success, name='booking_success'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointments/cancel/<int:pk>/', views.cancel_appointment, name='cancel_appointment'),
    path('services/', views.services, name='services'),
    path('team/', views.team, name='team'),
    path('dashboard/', views.barber_dashboard, name='barber_dashboard'),
    path('dashboard/action/<int:pk>/<str:action>/', views.barber_action, name='barber_action'),
    path('dashboard/rates/', views.shop_rates, name='shop_rates'),
    path('dashboard/slots/', views.shop_slots, name='shop_slots'),
    
    # Auth
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
