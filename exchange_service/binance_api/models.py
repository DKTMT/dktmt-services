from django.db import models
from cryptography.fernet import Fernet

from exchange_service.settings import ENCRYPTION_KEY, PUBLIC_KEY

import hmac
import hashlib

# Create your models here.
class UserAPI(models.Model):
    hashed_email = models.CharField(max_length=255, unique=True)
    exchange = models.CharField(max_length=255, unique=True)
    encrypted_api_key = models.TextField()
    encrypted_api_secret = models.TextField()
    
    def hash(self, data):
        """Hash the data using hmac""" 
        return hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'),
                        bytes(data, 'utf-8'),
                        digestmod=hashlib.sha256).hexdigest()
    
    def encrypt(self, data):
        """Encrypt the data using Fernet"""
        fernet = Fernet(PUBLIC_KEY)
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data.decode()

    def decrypt(self, data):
        """Decrypt the data using Fernet"""
        fernet = Fernet(PUBLIC_KEY)
        decrypted_data = fernet.decrypt(data.encode())
        return decrypted_data.decode()

    def save(self, *args, **kwargs):
        """Encrypt the API key and secret before saving to the database"""
        self.encrypted_api_key = self.encrypt(self.api_key)
        self.encrypted_api_secret = self.encrypt(self.api_secret)
        super().save(*args, **kwargs)

    @property
    def api_key(self):
        """Return the decrypted API key"""
        return self.decrypt(self.encrypted_api_key)

    @property
    def api_secret(self):
        """Return the decrypted API secret"""
        return self.decrypt(self.encrypted_api_secret)