from django.urls import path
from .views import customer_order

urlpatterns = [
    path("order/", customer_order, name="customer_order"),
]
