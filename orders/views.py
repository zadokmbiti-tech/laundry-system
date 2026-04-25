from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from services.models import Service
from .sms import send_order_received_sms, send_order_ready_sms


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order)

    total = sum(item.price for item in items)

    return render(request, "orders/order_detail.html", {
        "order": order,
        "items": items,
        "total": total,
    })


def home(request):
    return render(request, "home.html")


def customer_order(request):
    services = Service.objects.all()

    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        phone = request.POST.get("phone_number")
        selected_services = request.POST.getlist("services")

        order = Order.objects.create(
            customer_name=customer_name,
            phone_number=phone
        )

        for service_id in selected_services:
            service = Service.objects.get(id=service_id)

            quantity = request.POST.get(f"quantity_{service_id}")
            quantity = int(quantity) if quantity else 1

            OrderItem.objects.create(
                order=order,
                service=service,
                quantity=quantity,
                price=service.price * quantity
            )

        # ✅ Send "Order Received" SMS to customer
        send_order_received_sms(order)

        return redirect("order_detail", order_id=order.id)

    return render(request, "orders/customer_order.html", {"services": services})


# STAFF DASHBOARD
@login_required
def staff_dashboard(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "orders/staff_dashboard.html", {"orders": orders})


# STAFF UPDATE ORDER STATUS
@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        old_status = order.status

        print(f"[DEBUG] order={order.id} old_status={old_status} new_status={new_status}")

        order.status = new_status
        order.save()

        # ✅ Send "Order Ready" SMS when staff marks order as ready
        if new_status == "ready" and old_status != "ready":
            print(f"[DEBUG] Firing ready SMS to {order.phone_number}")
            result = send_order_ready_sms(order)
            print(f"[DEBUG] SMS result: {result}")
        else:
            print(f"[DEBUG] SMS not sent — new={new_status}, old={old_status}")

        return redirect("staff_dashboard")

    return render(request, "orders/update_order.html", {"order": order})