from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("<int:order_id>/", views.payment_page, name="payment_page"),
    path("process/<int:order_id>/", views.process_payment, name="process_payment"),
    path("callback/", views.mpesa_callback, name="mpesa_callback"),
    path("update-status/<int:payment_id>/", views.update_payment_status, name="update_payment_status"),
]