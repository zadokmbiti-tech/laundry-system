from django.urls import path
from .views import payment_page, process_payment, mpesa_callback

urlpatterns = [
    path("<int:order_id>/", payment_page, name="payment_page"),
    path("process/<int:order_id>/", process_payment, name="process_payment"),
    path("callback/", mpesa_callback, name="mpesa_callback"),
]
