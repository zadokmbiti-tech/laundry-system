# FreshWash — Laundry Management System

A full-stack Django web application for managing laundry operations at Maseno University. Built as a final year project (CIM 428), FreshWash digitizes order intake, staff management, payments, and customer notifications — with M-Pesa Daraja STK Push and Africa's Talking SMS/USSD integration.

🌐 **Live:** Deployed on Railway (precious-purpose/production)

---

## Features

### Customer
- Place laundry orders online or via USSD
- Pay via M-Pesa STK Push (Daraja API)
- Receive SMS notifications on order status updates
- PWA support — installable on mobile as an app

### Staff
- View and manage assigned orders
- Update order status (received → washing → ready → collected)
- Staff dashboard with daily task overview

### Admin
- Full order management
- Staff management and assignment
- Revenue and order reports
- SMS broadcast to customers

### Payments
- M-Pesa Daraja STK Push integration (sandbox tested)
- Token-based authentication with Safaricom API
- Payment confirmation via callback

### USSD
- Africa's Talking USSD integration
- Customers can place and check orders via USSD menu

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django (Python) |
| Database | PostgreSQL (Railway) |
| Frontend | HTML, CSS, JavaScript |
| Payments | M-Pesa Daraja STK Push |
| SMS/USSD | Africa's Talking |
| Deployment | Railway |
| PWA | Service Worker (`serviceworker.js`) |

---

## Project Structure

```
├── payments/           # M-Pesa Daraja STK Push logic
├── services/           # Laundry service definitions
├── staff/              # Staff management
├── static/images/      # Static assets
├── ussd/               # Africa's Talking USSD handler
├── manage.py
├── requirements.txt
├── Procfile            # Gunicorn for Railway deployment
└── serviceworker.js    # PWA service worker
```

---

## M-Pesa Integration

Uses `requests` library to interact with Safaricom Daraja API:

```python
# Token generation
response = requests.get(token_url, auth=(consumer_key, consumer_secret))

# STK Push
requests.post(stk_push_url, json=payload, headers=headers)
```

Sandbox tested with Safaricom test credentials. Callback URL configured for Railway deployment.

---

## Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Safaricom Daraja sandbox credentials
- Africa's Talking sandbox credentials

### Setup

```bash
git clone https://github.com/zadokmbiti-tech/laundry-system.git
cd laundry-system

pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Fill in DATABASE_URL, MPESA keys, AT keys, SECRET_KEY

python manage.py migrate
python manage.py runserver
```

---

## Academic Context

Built for **CIM 428** — Final Year Project, BSc ICT Management, Maseno University. The M-Pesa integration pattern developed here serves as the foundation for future POS system development.

---

## Developer

**Zadok Mutethia Mbiti**
- GitHub: [@zadokmbiti-tech](https://github.com/zadokmbiti-tech)
- Final year BSc ICT Management — Maseno University
