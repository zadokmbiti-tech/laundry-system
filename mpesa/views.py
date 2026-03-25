import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from .utils import stk_push
from .models import MpesaPayment
from orders.models import Order


def initiate_mpesa(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    phone = order.phone_number
    amount = order.total_price()

    result = stk_push(phone, amount, order_id)

    if result.get("ResponseCode") == "0":
        MpesaPayment.objects.create(
            order_id=order_id,
            checkout_request_id=result["CheckoutRequestID"],
            merchant_request_id=result["MerchantRequestID"],
            amount=amount,
            phone_number=phone,
        )
        return redirect("mpesa_waiting", order_id=order_id)
    else:
        return render(request, "payments/payment_page.html", {
            "order": order,
            "error": result.get("errorMessage", "STK push failed. Please try again.")
        })


def mpesa_wait(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "payments/mpesa_wait.html", {
        "order_id": order_id,
        "order": order
    })


def mpesa_status(request, order_id):
    payment = MpesaPayment.objects.filter(order_id=order_id).order_by("-created_at").first()
    if not payment:
        return JsonResponse({"status": "pending"})
    return JsonResponse({
        "status": payment.status,
        "receipt": payment.mpesa_receipt or ""
    })


@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    callback = data["Body"]["stkCallback"]

    checkout_request_id = callback["CheckoutRequestID"]
    result_code = callback["ResultCode"]

    try:
        payment = MpesaPayment.objects.get(checkout_request_id=checkout_request_id)
        if result_code == 0:
            items = {i["Name"]: i["Value"] for i in callback["CallbackMetadata"]["Item"]}
            payment.status = "success"
            payment.mpesa_receipt = items.get("MpesaReceiptNumber", "")
        else:
            payment.status = "failed"
        payment.save()
    except MpesaPayment.DoesNotExist:
        pass

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})