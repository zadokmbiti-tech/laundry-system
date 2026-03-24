from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("order/", views.customer_order, name="customer_order"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/update-status/<int:order_id>/", views.update_order_status, name="update_order"),  # ✅ matches template
]