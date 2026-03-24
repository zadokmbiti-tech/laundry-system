from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('update/<int:order_id>/', views.update_order_status, name='update_order'),
    path('customers/', views.customer_details, name='customer_details'),
    path('create/', views.create_order, name='create_order'),
    path('report/', views.generate_report, name='generate_report'),
]