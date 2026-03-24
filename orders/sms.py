import os
os.environ['PYTHONHTTPSVERIFY'] = '0'

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import africastalking

AT_USERNAME = 'sandbox'
AT_API_KEY  = 'atsk_86b41a4d46f39eed365e617a784ce0caf519d4570a7e24883e9a443e28cc6e0c6d3be670'

def initialize_sms():
    """Initialize Africa's Talking SDK."""
    africastalking.initialize(
        username=AT_USERNAME,
        api_key=AT_API_KEY,
    )
    return africastalking.SMS


def send_order_received_sms(order):
    """
    Send SMS to customer when their order is received.
    Called immediately after a new order is created.
    """
    try:
        sms = initialize_sms()

        # Build a summary of services ordered
        items = order.items.select_related('service').all()
        service_list = ', '.join(
            f"{item.service.name} x{item.quantity}" for item in items
        )

        message = (
            f"Hi {order.customer_name}, your FreshWash order #{order.id} has been received!\n"
            f"Services: {service_list}\n"
            f"We will notify you when it is ready. Thank you!"
        )

        phone = order.phone_number
        # Ensure phone is in international format for Kenya (+254...)
        if phone.startswith('0'):
            phone = '+254' + phone[1:]

        response = sms.send(message, [phone])
        print(f"[SMS] Order received sent to {phone}: {response}")
        return True

    except Exception as e:
        print(f"[SMS ERROR] Could not send order received SMS: {e}")
        return False


def send_order_ready_sms(order):
    """
    Send SMS to customer when their order is ready for pickup.
    Called when staff updates order status to 'ready'.
    """
    try:
        sms = initialize_sms()

        message = (
            f"Hi {order.customer_name}, your FreshWash order #{order.id} is READY for pickup!\n"
            f"Pickup address: {order.pickup_address}\n"
            f"Please collect your laundry at your earliest convenience. Thank you!"
        )

        phone = order.phone_number
        if phone.startswith('0'):
            phone = '+254' + phone[1:]

        response = sms.send(message, [phone])
        print(f"[SMS] Order ready sent to {phone}: {response}")
        return True

    except Exception as e:
        print(f"[SMS ERROR] Could not send order ready SMS: {e}")
        return False