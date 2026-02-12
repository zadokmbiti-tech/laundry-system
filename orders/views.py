from django.shortcuts import render, redirect
from .models import Order, OrderItem
from services.models import Service


def customer_order(request):
    services = Service.objects.all()

    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        phone = request.POST.get("phone_number")
        selected_services = request.POST.getlist("services")

        order = Order.objects.create( customer_name=customer_name, phone_number=phone)

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

        return redirect("payment_page", order_id=order.id)

    return render(request, "orders/customer_order.html", {"services": services})
