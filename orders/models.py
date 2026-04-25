from django.db import models
from services.models import Service
from decimal import Decimal, InvalidOperation


class Order(models.Model):
    STATUS_CHOICES = (
        ('received', 'Received'),
        ('washing', 'Washing'),
        ('drying', 'Drying'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
    )

    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='received'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        total = Decimal('0.00')
        try:
            for item in self.items.select_related('service').all():
                try:
                    total += item.total_price()
                except (InvalidOperation, TypeError, ValueError, Exception):
                    continue
        except Exception:
            return Decimal('0.00')
        return total

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def total_price(self):
        try:
            return Decimal(str(self.service.price)) * self.quantity
        except (InvalidOperation, TypeError, ValueError, AttributeError):
            return Decimal('0.00')

    def __str__(self):
        return f"{self.service.name} x{self.quantity}"