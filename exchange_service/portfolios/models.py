from django.utils import timezone
from django.db import models
from exchange_service.settings import ENCRYPTION_KEY

import hmac
import hashlib


class Portfolio(models.Model):
    hashed_email = models.CharField(max_length=255)
    exchange = models.CharField(max_length=64)
    port_value = models.FloatField()
    coins_possess = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def hash(self, data):
        """Hash the data using hmac""" 
        return hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'),
                        bytes(data, 'utf-8'),
                        digestmod=hashlib.sha256).hexdigest()