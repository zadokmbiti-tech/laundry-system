import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Payment
from orders.models import Order


@login_required(login_url='staff_login')
@require_POST
def update_payment_status(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    new_status = request.POST.get('status')
    if new_status in ['paid', 'pending', 'failed']:
        payment.status = new_status
        payment.save()
        messages.success(request, f'Payment #{payment.id} status updated to {new_status}.')
    return redirect('staff_dashboard')


@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            callback = data["Body"]["stkCallback"]
            result_code = callback["ResultCode"]
            checkout_id = callback["CheckoutRequestID"]
            payment = Payment.objects.filter(checkout_request_id=checkout_id).first()
            if payment:
                payment.status = "paid" if result_code == 0 else "failed"
                payment.save()
        except Exception as e:
            print("MPESA CALLBACK ERROR:", e)
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    return JsonResponse({"error": "Invalid request"}, status=400)


def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "payments/payment_page.html", {
        "order": order,
        "customer_name": order.customer_name,
        "phone": order.phone_number,
    })


def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        method = request.POST.get("method")
        payment = Payment.objects.create(
            order=order,
            payment_method=method,
            phone_number=order.phone_number,
        )
        if method == "CASH":
            payment.status = "paid"
            payment.save()
            return render(request, "payments/success.html", {"order": order})
        elif method == "BANK":
            return render(request, "payments/bank_details.html", {"order": order})
        elif method == "MPESA":
            return render(request, "payments/mpesa_wait.html", {"order": order})

    return render(request, "payments/payment_page.html", {
        "order": order,
        "customer_name": order.customer_name,
        "phone": order.phone_number,
    })