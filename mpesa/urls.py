from django.urls import path
from . import views

urlpatterns = [
    path("initiate/<int:order_id>/", views.initiate_mpesa, name="mpesa_initiate"),
    path("waiting/<int:order_id>/",  views.mpesa_wait,  name="mpesa_waiting"),
    path("status/<int:order_id>/",   views.mpesa_status,   name="mpesa_status"),
    path("callback/",                views.mpesa_callback, name="mpesa_callback"),
]