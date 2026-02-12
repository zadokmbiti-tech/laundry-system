import requests
import base64
from datetime import datetime

# Daraja sandbox credentials
CONSUMER_KEY = "8wGhceuFGAfuwtSNSZNuoMUwCvadwDHKX4EZZ7q9Y307aeAk"
CONSUMER_SECRET = "bP0lt6Asg77ZagLdg4fEWFafCegtLJ0gTzx4pGxugG1wb64A7vzcQnzDo6r4rU63"
BUSINESS_SHORT_CODE = "174379"   # sandbox shortcode
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
CALLBACK_URL = "https://example.com/mpesa/callback/"


def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json()['access_token']


def stk_push(phone, amount, account_ref):
    access_token = get_access_token()

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = BUSINESS_SHORT_CODE + PASSKEY + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": BUSINESS_SHORT_CODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": BUSINESS_SHORT_CODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": "Laundry Payment"
    }

    response = requests.post(url, json=payload, headers=headers)
    print("MPESA RESPONSE:", response.text)
    return response.json()
