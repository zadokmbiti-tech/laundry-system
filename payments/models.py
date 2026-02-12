from django.db import models
from orders.models import Order   


class Payment(models.Model):
    METHOD_CHOICES = (
        ("CASH", "Cash"),
        ("MPESA", "M-pesa"),
        ("BANK", "Bank"),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    paid_at = models.DateTimeField(auto_now_add=True)

    checkout_request_id = models.CharField(
    max_length=100,
    blank=True,
    null=True
)


    def save(self, *args, **kwargs):
        if self.order:
            self.amount = self.order.total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment for Order {self.order.id}"