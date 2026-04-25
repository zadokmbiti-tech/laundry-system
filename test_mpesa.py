import requests
import os

# Clear any proxy settings
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('https_proxy', None)
os.environ.pop('http_proxy', None)

session = requests.Session()
session.trust_env = False  # ignore system proxy completely
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
})

r = session.get(
    'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
    auth=('P0gNiGG5eT1oZmcWxRn6laXJk9zqf3kS583NMaEXYRhsNDGf', '5ks1YG8M56YoKWAkwXY9lMCaljq1qqG9rh0rSGglnnQBAiyEKGHY3PMBnd0Bq0qO'),
)
print("Status:", r.status_code)
print("Body:", r.text)