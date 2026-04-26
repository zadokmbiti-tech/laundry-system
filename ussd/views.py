from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from orders.models import Order, OrderItem
from services.models import Service
from django.utils import timezone

SERVICES_PER_PAGE = 5
STAFF_PIN = '0011'


def get_services_page(page):
    services = list(Service.objects.all())
    start = (page - 1) * SERVICES_PER_PAGE
    end = start + SERVICES_PER_PAGE
    page_services = services[start:end]
    has_more = end < len(services)
    return page_services, has_more, start


@csrf_exempt
def ussd_callback(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phoneNumber', '')
        text         = request.POST.get('text', '')

        text_parts = text.split('*') if text else ['']
        level = len(text_parts)

        # ── LEVEL 0 — Main Menu ──────────────────────────────────────────
        if text == '':
            response  = "CON Welcome to FreshWash\n"
            response += "1. Customer Menu\n"
            response += "2. Staff Menu"

        # ── CUSTOMER MENU ────────────────────────────────────────────────
        elif text == '1':
            response  = "CON Customer Menu\n"
            response += "1. Place a New Order\n"
            response += "2. Check Order Status\n"
            response += "3. Make a Payment\n"
            response += "4. View Services & Prices"

        # ── STAFF MENU ───────────────────────────────────────────────────
        elif text == '2':
            response = "CON Staff Menu\nEnter your PIN:"

        # ── STAFF PIN CHECK ──────────────────────────────────────────────
        elif level == 2 and text_parts[0] == '2':
            pin = text_parts[1]
            if pin == STAFF_PIN:
                response  = "CON Staff Dashboard\n"
                response += "1. View Today's Orders\n"
                response += "2. Update Order Status\n"
                response += "3. View Today's Revenue"
            else:
                response = "END Invalid PIN. Access denied."

        # ── STAFF: VIEW TODAY'S ORDERS ───────────────────────────────────
        elif level == 3 and text_parts[0] == '2' and text_parts[2] == '1':
            today = timezone.now().date()
            orders = Order.objects.filter(created_at__date=today).order_by('-id')[:5]
            if orders.exists():
                response = "END Today's Orders:\n"
                for o in orders:
                    response += f"#{o.id} {o.customer_name} - {o.status.upper()}\n"
            else:
                response = "END No orders today yet."

        # ── STAFF: UPDATE ORDER STATUS — ask order ID ────────────────────
        elif level == 3 and text_parts[0] == '2' and text_parts[2] == '2':
            response = "CON Enter Order ID to update:"

        # ── STAFF: GOT ORDER ID — show status options ────────────────────
        elif level == 4 and text_parts[0] == '2' and text_parts[2] == '2':
            order_id = text_parts[3]
            try:
                order = Order.objects.get(id=order_id)
                response  = f"CON Order #{order.id} - {order.customer_name}\n"
                response += f"Current: {order.status.upper()}\n"
                response += "Update to:\n"
                response += "1. Received\n"
                response += "2. Washing\n"
                response += "3. Drying\n"
                response += "4. Ready\n"
                response += "5. Delivered"
            except Order.DoesNotExist:
                response = f"END Order #{order_id} not found."

        # ── STAFF: GOT NEW STATUS — update order ─────────────────────────
        elif level == 5 and text_parts[0] == '2' and text_parts[2] == '2':
            order_id   = text_parts[3]
            status_map = {
                '1': 'received',
                '2': 'washing',
                '3': 'drying',
                '4': 'ready',
                '5': 'delivered',
            }
            new_status = status_map.get(text_parts[4])
            try:
                order = Order.objects.get(id=order_id)
                if new_status:
                    order.status = new_status
                    order.save()
                    response  = f"END Order #{order.id} updated!\n"
                    response += f"Status: {new_status.upper()}\n"
                    response += f"Customer: {order.customer_name}"
                else:
                    response = "END Invalid status selection."
            except Order.DoesNotExist:
                response = f"END Order #{order_id} not found."

        # ── STAFF: VIEW TODAY'S REVENUE ──────────────────────────────────
        elif level == 3 and text_parts[0] == '2' and text_parts[2] == '3':
            today = timezone.now().date()
            orders = Order.objects.filter(created_at__date=today)
            total_revenue = sum(o.total_price() for o in orders)
            total_orders  = orders.count()
            response  = "END Today's Summary:\n"
            response += f"Orders: {total_orders}\n"
            response += f"Revenue: KSh {total_revenue}\n"
            response += f"Date: {today.strftime('%d %b %Y')}"

        # ── CUSTOMER SUBMENU ─────────────────────────────────────────────
        elif text == '1*1':
            response = "CON Enter your Full Name:"

        elif text == '1*2':
            response = "CON Enter your Order ID:"

        elif text == '1*3':
            response = "CON Enter your Order ID to pay:"

        elif text == '1*4':
            page_services, has_more, _ = get_services_page(1)
            if page_services:
                response = "CON Services & Prices:\n"
                for i, s in enumerate(page_services, start=1):
                    response += f"{i}. {s.name} KSh{s.price}\n"
                if has_more:
                    response += "6. More..."
                else:
                    response = response.replace("CON", "END")
            else:
                response = "END No services available."

        # ── PLACE ORDER FLOW ─────────────────────────────────────────────
        elif level == 3 and text_parts[0] == '1' and text_parts[1] == '1':
            response = "CON Enter your Phone Number\n(e.g. 0712345678):"

        elif level == 4 and text_parts[0] == '1' and text_parts[1] == '1':
            page_services, has_more, _ = get_services_page(1)
            if page_services:
                response = "CON Select a Service:\n"
                for i, s in enumerate(page_services, start=1):
                    response += f"{i}. {s.name} KSh{s.price}\n"
                if has_more:
                    response += "6. More..."
            else:
                response = "END No services available."

        elif level == 5 and text_parts[0] == '1' and text_parts[1] == '1' and text_parts[4] == '6':
            page_services, has_more, _ = get_services_page(2)
            if page_services:
                response = "CON Select a Service (2):\n"
                for i, s in enumerate(page_services, start=1):
                    response += f"{i}. {s.name} KSh{s.price}\n"
                if has_more:
                    response += "6. More..."
            else:
                response = "END No more services."

        elif level == 5 and text_parts[0] == '1' and text_parts[1] == '1':
            response = "CON Enter Quantity\n(number of items):"

        elif level == 6 and text_parts[0] == '1' and text_parts[1] == '1' and text_parts[4] == '6':
            response = "CON Enter Quantity\n(number of items):"

        elif level == 6 and text_parts[0] == '1' and text_parts[1] == '1':
            customer_name  = text_parts[2]
            customer_phone = text_parts[3]
            service_index  = int(text_parts[4]) - 1
            quantity       = int(text_parts[5])
            try:
                services = list(Service.objects.all())
                service  = services[service_index]
                order = Order.objects.create(
                    customer_name=customer_name,
                    phone_number=customer_phone,
                    status='received',
                )
                OrderItem.objects.create(
                    order=order,
                    service=service,
                    quantity=quantity,
                    price=service.price,
                )
                total = service.price * quantity
                response  = "END Order placed!\n"
                response += f"Order ID: #{order.id}\n"
                response += f"Service: {service.name}\n"
                response += f"Qty: {quantity}\n"
                response += f"Total: KSh {total}\n"
                response += "Thank you for choosing FreshWash!"
            except Exception as e:
                response = f"END Error: {str(e)}"

        elif level == 7 and text_parts[0] == '1' and text_parts[1] == '1' and text_parts[4] == '6':
            customer_name  = text_parts[2]
            customer_phone = text_parts[3]
            service_index  = int(text_parts[5]) - 1 + SERVICES_PER_PAGE
            quantity       = int(text_parts[6])
            try:
                services = list(Service.objects.all())
                service  = services[service_index]
                order = Order.objects.create(
                    customer_name=customer_name,
                    phone_number=customer_phone,
                    status='received',
                )
                OrderItem.objects.create(
                    order=order,
                    service=service,
                    quantity=quantity,
                    price=service.price,
                )
                total = service.price * quantity
                response  = "END Order placed!\n"
                response += f"Order ID: #{order.id}\n"
                response += f"Service: {service.name}\n"
                response += f"Qty: {quantity}\n"
                response += f"Total: KSh {total}\n"
                response += "Thank you for choosing FreshWash!"
            except Exception as e:
                response = f"END Error: {str(e)}"

        # ── CHECK ORDER STATUS ────────────────────────────────────────────
        elif level == 3 and text_parts[0] == '1' and text_parts[1] == '2':
            order_id = text_parts[2]
            try:
                order = Order.objects.get(id=order_id)
                total = order.total_price()
                first_item = order.items.first()
                service_name = first_item.service.name if first_item else "N/A"
                response  = f"END Order #{order.id}\n"
                response += f"Name: {order.customer_name}\n"
                response += f"Service: {service_name}\n"
                response += f"Status: {order.status.upper()}\n"
                response += f"Total: KSh {total}"
            except Order.DoesNotExist:
                response = f"END Order #{order_id} not found."

        # ── PAYMENT FLOW ──────────────────────────────────────────────────
        elif level == 3 and text_parts[0] == '1' and text_parts[1] == '3':
            order_id = text_parts[2]
            try:
                order = Order.objects.get(id=order_id)
                total = order.total_price()

                # Format phone number to 2547XXXXXXXX
                phone = order.phone_number.strip().replace('+', '').replace(' ', '')
                if phone.startswith('0'):
                    phone = '254' + phone[1:]

                # Trigger real STK push
                from payments.mpesa import stk_push
                from payments.models import Payment, MpesaPayment

                result = stk_push(phone, total, order.id)

                if result.get("ResponseCode") == "0":
                    MpesaPayment.objects.create(
                        order_id=order.id,
                        checkout_request_id=result["CheckoutRequestID"],
                        merchant_request_id=result["MerchantRequestID"],
                        amount=total,
                        phone_number=phone,
                        status="pending",
                    )
                    response  = "END Payment request sent!\n"
                    response += f"Order #{order.id} - KSh {total}\n"
                    response += "Check your phone for M-Pesa prompt.\n"
                    response += "Thank you for using FreshWash!"
                else:
                    error = result.get("errorMessage") or result.get("ResponseDescription", "Failed")
                    response = f"END Payment failed: {error}"

            except Order.DoesNotExist:
                response = f"END Order #{order_id} not found."
            except Exception as e:
                response = f"END Payment error: {str(e)}"

        # ── FALLBACK ──────────────────────────────────────────────────────
        else:
            response = "END Invalid selection. Please try again."

        return HttpResponse(response, content_type='text/plain')

    return HttpResponse("Method not allowed", status=405)