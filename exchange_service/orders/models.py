from django.db import models
from exchange_service.utils import encrypt, decrypt

# Create your views here.
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    hashed_email = models.CharField(max_length=100)
    exchange = models.CharField(max_length=255)
    order_symbol = models.CharField(max_length=20)
    order_side = models.CharField(max_length=4)
    order_amount = models.DecimalField(max_digits=20, decimal_places=10)
    order_value = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return self.order_id