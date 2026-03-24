from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from decimal import Decimal
import csv

from orders.models import Order
from payments.models import Payment

User = get_user_model()


def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if hasattr(user, 'staffprofile'):
                login(request, user)
                return redirect('staff_dashboard')
            else:
                messages.error(request, 'This account is not a staff account.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'staff/login.html')


def staff_logout(request):
    logout(request)
    return redirect('staff_login')


@login_required(login_url='staff_login')
def staff_dashboard(request):
    limit = request.GET.get('limit', '10')

    all_orders = Order.objects.all().order_by('-created_at')
    all_payments = Payment.objects.all().order_by('-paid_at')

    today = timezone.now().date()

    total_customers = Order.objects.filter(
        created_at__date=today
    ).values('phone_number').distinct().count()

    received_orders = all_orders.filter(status='received').count()
    washing_orders = all_orders.filter(status='washing').count()
    ready_orders = all_orders.filter(status='ready').count()
    delivered_orders = all_orders.filter(status='delivered').count()

    today_revenue = all_payments.filter(
        status='paid',
        paid_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    orders = all_orders
    payments = all_payments

    if limit != 'all':
        try:
            limit_int = int(limit)
            orders = all_orders[:limit_int]
            payments = all_payments[:limit_int]
        except ValueError:
            orders = all_orders[:10]
            payments = all_payments[:10]
            limit = '10'

    context = {
        'orders': orders,
        'payments': payments,
        'limit': limit,

        'total_orders': all_orders.count(),
        'today_orders': all_orders.filter(created_at__date=today).count(),
        'total_customers': total_customers,
        'today_revenue': today_revenue,
        'pending_payments': all_payments.filter(status='pending').count(),

        'received_orders': received_orders,
        'washing_orders': washing_orders,
        'ready_orders': ready_orders,
        'delivered_orders': delivered_orders,
    }

    return render(request, 'staff/dashboard.html', context)


@login_required(login_url='staff_login')
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order {order.id} status updated.')
        return redirect('staff_dashboard')

    return render(request, 'staff/update_order.html', {'order': order})


@login_required(login_url='staff_login')
def customer_details(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'staff/customers.html', {'orders': orders})


@login_required(login_url='staff_login')
def create_order(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        phone = request.POST.get('phone_number')
        total = request.POST.get('total_price')

        Order.objects.create(
            customer_name=customer_name,
            phone_number=phone,
            total_price=total,
            status='received'
        )
        return redirect('staff_dashboard')

    return render(request, 'staff/create_order.html')


@login_required(login_url='staff_login')
def generate_report(request):
    period = request.GET.get('period', 'daily')
    fmt    = request.GET.get('format', 'csv')

    today = timezone.now().date()

    if period == 'daily':
        start = today
    elif period == 'weekly':
        start = today - timedelta(days=7)
    else:  # monthly
        start = today.replace(day=1)

    orders = Order.objects.filter(created_at__date__gte=start).order_by('-created_at')
    payments = Payment.objects.filter(paid_at__date__gte=start, status='paid')

    revenue = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    by_status = {
        'Received':  orders.filter(status='received').count(),
        'Washing':   orders.filter(status='washing').count(),
        'Ready':     orders.filter(status='ready').count(),
        'Delivered': orders.filter(status='delivered').count(),
    }

    if fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{period}_report_{today}.csv"'
        writer = csv.writer(response)
        writer.writerow(['#', 'Customer Name', 'Phone', 'Total (KSh)', 'Status', 'Date'])
        for o in orders:
            writer.writerow([
                o.id,
                o.customer_name,
                o.phone_number,
                o.total_price,
                o.status,
                o.created_at.strftime('%d %b %Y'),
            ])
        return response

    # Print/HTML view
    context = {
        'orders': orders,
        'period': period,
        'start': start,
        'today': today,
        'revenue': revenue,
        'by_status': by_status,
    }
    return render(request, 'staff/report.html', context)