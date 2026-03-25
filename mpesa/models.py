from django.db import models

class MpesaPayment(models.Model):
    order_id = models.IntegerField()
    checkout_request_id = models.CharField(max_length=200, unique=True)
    merchant_request_id = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default="pending")  # pending, success, failed
    mpesa_receipt = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"