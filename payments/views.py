import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Payment, MpesaPayment
from orders.models import Order
from .mpesa import stk_push


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
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        callback = data["Body"]["stkCallback"]
        result_code = callback["ResultCode"]
        result_desc = callback.get("ResultDesc", "")
        checkout_id = callback["CheckoutRequestID"]

        mpesa_payment = MpesaPayment.objects.filter(checkout_request_id=checkout_id).first()
        if mpesa_payment:
            if result_code == 0:
                items = callback["CallbackMetadata"]["Item"]
                meta = {item["Name"]: item.get("Value") for item in items}
                mpesa_payment.status = "success"
                mpesa_payment.mpesa_receipt_number = meta.get("MpesaReceiptNumber", "")
            else:
                mpesa_payment.status = "failed" if result_code != 1032 else "cancelled"
            mpesa_payment.result_desc = result_desc
            mpesa_payment.save()

        payment = Payment.objects.filter(checkout_request_id=checkout_id).first()
        if payment:
            payment.status = "paid" if result_code == 0 else "failed"
            payment.save()

    except Exception as e:
        print("MPESA CALLBACK ERROR:", e)

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


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

        if method == "CASH":
            Payment.objects.create(
                order=order,
                payment_method="CASH",
                phone_number=order.phone_number,
                status="paid",
            )
            return redirect('payments:receipt', order_id=order.id)

        elif method == "MPESA":
            phone = order.phone_number.replace('+', '').replace(' ', '')
            amount = order.total_price()

            print(f"[MPESA] Initiating STK Push → phone={phone}, amount={amount}")

            try:
                result = stk_push(phone, amount, order.id)
            except Exception as e:
                print(f"[MPESA ERROR] {str(e)}")
                messages.error(request, f"M-Pesa error: {str(e)}")
                return redirect('payments:payment_page', order_id=order.id)

            print(f"[MPESA] STK Response: {result}")

            if result.get("ResponseCode") == "0":
                MpesaPayment.objects.create(
                    order_id=order.id,
                    checkout_request_id=result["CheckoutRequestID"],
                    merchant_request_id=result["MerchantRequestID"],
                    amount=amount,
                    phone_number=phone,
                    status="pending",
                )
                Payment.objects.create(
                    order=order,
                    payment_method="MPESA",
                    phone_number=phone,
                    checkout_request_id=result["CheckoutRequestID"],
                    status="pending",
                )
                return redirect('payments:mpesa_waiting', order_id=order.id)
            else:
                error = result.get("errorMessage") or result.get("ResponseDescription", "STK Push failed. Try again.")
                messages.error(request, error)
                return redirect('payments:payment_page', order_id=order.id)

    return render(request, "payments/payment_page.html", {
        "order": order,
        "customer_name": order.customer_name,
        "phone": order.phone_number,
    })


def receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment = order.payment_set.order_by('-id').first()
    return render(request, "payments/receipt.html", {
        "order": order,
        "payment": payment,
    })


def mpesa_waiting(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "payments/mpesa_wait.html", {"order": order})


def mpesa_status(request, order_id):
    payment = MpesaPayment.objects.filter(order_id=order_id).order_by("-created_at").first()
    if not payment:
        return JsonResponse({"status": "pending"})
    return JsonResponse({
        "status": payment.status,
        "receipt": payment.mpesa_receipt_number or ""
    })