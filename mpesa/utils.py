import requests
import base64
from datetime import datetime
from django.conf import settings


def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(
        settings.MPESA_CONSUMER_KEY,
        settings.MPESA_CONSUMER_SECRET
    ))
    return response.json().get("access_token")


def generate_password():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    encoded = base64.b64encode(raw.encode()).decode()
    return encoded, timestamp


def stk_push(phone_number, amount, order_id):
    access_token = get_access_token()
    password, timestamp = generate_password()

    # Normalize phone: 0786... -> 254786...
    if phone_number.startswith("0"):
        phone_number = "254" + phone_number[1:]
    elif phone_number.startswith("+"):
        phone_number = phone_number[1:]

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"Order{order_id}",
        "TransactionDesc": f"FreshWash Order {order_id}"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )
    return response.json()