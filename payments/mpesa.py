import json
import urllib.request
import base64 as b64lib
from datetime import datetime
from django.conf import settings


def get_access_token():
    key = settings.MPESA_CONSUMER_KEY
    secret = settings.MPESA_CONSUMER_SECRET
    credentials = b64lib.b64encode(f"{key}:{secret}".encode()).decode()

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Basic {credentials}")
    req.add_header("User-Agent", "python-urllib/3.11")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            print(f"[MPESA TOKEN] Got token: {data.get('access_token', '')[:20]}...")
            return data['access_token']
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise Exception(f"Token request failed: {e.code} - {body}")
    except Exception as e:
        raise Exception(f"Token request error: {str(e)}")


def generate_password():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    password = b64lib.b64encode(raw.encode()).decode()
    return password, timestamp


def stk_push(phone_number, amount, order_id):
    """
    Triggers STK push to customer phone.
    phone_number: format 2547XXXXXXXX (no + sign)
    """
    access_token = get_access_token()
    password, timestamp = generate_password()

    import requests
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
        "AccountReference": f"FreshWash-{order_id}",
        "TransactionDesc": f"Payment for Order #{order_id}"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )
    print(f"[MPESA STK] Status: {response.status_code} | Body: {response.text}")
    return response.json()