from django.contrib import admin
from django.urls import path, include
from orders.views import home
from services.views import services_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('staff/', include('staff.urls')),
    path('', include('pwa.urls')),
    path('', include('ussd.urls')),
    path('services/', services_view, name='services'),
    path('payments/mpesa/', include('mpesa.urls')),
]