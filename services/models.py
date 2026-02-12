from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="No description")
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name
