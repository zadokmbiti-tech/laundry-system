from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("<int:order_id>/", views.payment_page, name="payment_page"),
    path("process/<int:order_id>/", views.process_payment, name="process_payment"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
    path("mpesa/waiting/<int:order_id>/", views.mpesa_waiting, name="mpesa_waiting"),
    path("update-status/<int:payment_id>/", views.update_payment_status, name="update_payment_status"),
    path("receipt/<int:order_id>/", views.receipt, name="receipt"),
    path("mpesa/status/<int:order_id>/", views.mpesa_status, name="mpesa_status"),
]