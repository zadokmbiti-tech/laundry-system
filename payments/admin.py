from django.contrib import admin
from .models import Payment, MpesaPayment

admin.site.register(Payment)
admin.site.register(MpesaPayment)