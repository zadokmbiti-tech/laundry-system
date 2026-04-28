import os
import ssl

# ── SSL bypass ────────────────────────────────────────────────────────────────
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context
# ─────────────────────────────────────────────────────────────────────────────

import urllib.request
import urllib.parse
import json
from django.conf import settings

def _send_sms(message: str, phone: str) -> bool:
    print(f"[DEBUG] USERNAME={settings.AT_USERNAME}")
    print(f"[DEBUG] API_KEY={settings.AT_API_KEY[:20]}...")  # only first 20 chars
    url = "https://api.sandbox.africastalking.com/version1/messaging"


def normalise_phone(phone: str) -> str:
    """Convert 07XXXXXXXX to +2547XXXXXXXX."""
    phone = phone.strip().replace(" ", "")
    if phone.startswith("0"):
        return "+254" + phone[1:]
    elif phone.startswith("254"):
        return "+" + phone
    elif not phone.startswith("+"):
        return "+254" + phone
    return phone


def _send_sms(message: str, phone: str) -> bool:
    url = "https://api.sandbox.africastalking.com/version1/messaging"

    payload = urllib.parse.urlencode({
        "username": settings.AT_USERNAME,
        "to":       phone,
        "message":  message,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("apiKey",       settings.AT_API_KEY)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept",       "application/json")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        body = json.loads(resp.read().decode())
        print(f"[SMS] Sent to {phone}: {body}")
        return True


def send_order_received_sms(order):
    """Send 'Order Received' SMS to customer and notify owner."""
    try:
        items = order.items.select_related('service').all()
        service_list = ', '.join(
            f"{item.service.name} x{item.quantity}" for item in items
        )

        # SMS to customer
        customer_message = (
            f"Hi {order.customer_name}, your FreshWash order #{order.id} has been received!\n"
            f"Services: {service_list}\n"
            f"We will notify you when it is ready. Thank you!"
        )
        _send_sms(customer_message, normalise_phone(order.phone_number))

        # SMS to owner
        owner_phone = getattr(settings, 'OWNER_PHONE', None)
        if owner_phone:
            owner_message = (
                f"New order #{order.id} received!\n"
                f"Customer: {order.customer_name} ({order.phone_number})\n"
                f"Services: {service_list}\n"
                f"Total: KES {order.total_price()}"
            )
            _send_sms(owner_message, normalise_phone(owner_phone))

        return True

    except Exception as e:
        print(f"[SMS ERROR] Could not send order received SMS: {e}")
        return False


def send_order_ready_sms(order):
    """Send 'Order Ready' SMS when staff marks the order ready for pickup."""
    try:
        message = (
            f"Hi {order.customer_name}, your FreshWash order #{order.id} is READY for pickup!\n"
            f"Please collect your laundry at your earliest convenience. Thank you!"
        )
        return _send_sms(message, normalise_phone(order.phone_number))

    except Exception as e:
        print(f"[SMS ERROR] Could not send order ready SMS: {e}")
        return False