from django.db import models
from exchange_service.utils import encrypt, decrypt

# Create your models here.
class UserAPI(models.Model):
    hashed_email = models.CharField(max_length=255, unique=True)
    exchange = models.CharField(max_length=255)
    encrypted_api_key = models.TextField()
    encrypted_api_secret = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Encrypt the API key and secret before saving to the database"""
        self.encrypted_api_key = encrypt(self.api_key)
        self.encrypted_api_secret = encrypt(self.api_secret)
        super().save(*args, **kwargs)

    @property
    def api_key(self):
        """Return the decrypted API key"""
        return decrypt(self.encrypted_api_key)

    @property
    def api_secret(self):
        """Return the decrypted API secret"""
        return decrypt(self.encrypted_api_secret)
    
class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    hashed_email = models.CharField(max_length=255)
    exchange_type = models.CharField(max_length=255)
    order_type = models.CharField(max_length=4, choices=(('buy', 'Buy'), ('sell', 'Sell')))
    order_id = models.CharField(max_length=255)
    order_value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    