from django.db import models
from django.utils import timezone

class Ticket(models.Model):
    TICKET_STATUS_CHOICES = [
        ('O', 'Open'),
        ('C', 'Closed'),
    ]
    TICKET_TYPE_CHOICES = [
        ('P', 'Predict'),
        ('O', 'Order'),
    ]
    EXCHANGE_CHOICES = [
        ('B', 'Binance'),
        ('K', 'Kraken'),
        ('C', 'Coinbase'),
        ('T', 'Bitkub'),
    ]
    DURATION_UNIT_CHOICES = [
        ('T', 'Times'),
        ('D', 'Days'),
    ]
    ticket_id = models.AutoField(primary_key=True)
    ticket_type =  models.CharField(max_length=1, choices=TICKET_TYPE_CHOICES)
    ticket_status = models.CharField(max_length=1, choices=TICKET_STATUS_CHOICES, default='O')
    hashed_email = models.CharField(max_length=100)
    exchange = models.CharField(max_length=1, choices=EXCHANGE_CHOICES)
    duration_unit = models.CharField(max_length=1, choices=DURATION_UNIT_CHOICES)
    duration_value = models.PositiveSmallIntegerField() #ensures that the value is positive and fits within a 16-bit signed integer
    time_frame = models.CharField(max_length=3)
    budget = models.DecimalField(max_digits=20, decimal_places=10)
    conditions = models.JSONField() #condition like stoploss or take profit
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticket_id
