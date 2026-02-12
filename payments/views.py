import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from .models import Payment
from orders.models import Order


@csrf_exempt
def mpesa_callback(request):
    """
    Receives MPESA STK push callback.
    Updates payment status automatically.
    """
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            callback = data["Body"]["stkCallback"]
            result_code = callback["ResultCode"]
            checkout_id = callback["CheckoutRequestID"]

            # Find payment using CheckoutRequestID
            payment = Payment.objects.filter(
                checkout_request_id=checkout_id
            ).first()

            if payment:
                if result_code == 0:
                    payment.status = "PAID"
                else:
                    payment.status = "FAILED"

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

        # Handle different payment methods
        if method == "CASH":
            payment.status = "paid"
            payment.save()
            return render(request, "payments/success.html", {"order": order})

        elif method == "BANK":
            return render(request, "payments/bank_details.html", {"order": order})

        elif method == "MPESA":
            return render(request, "payments/mpesa_wait.html", {"order": order})

    # fallback
    return render(request, "payments/payment_page.html", {
        "order": order,
        "customer_name": order.customer_name,
        "phone": order.phone_number,
    })
