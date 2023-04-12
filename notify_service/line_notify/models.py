from django.db import models
import hashlib
import hmac
from notify_service.settings import ENCRYPTION_KEY

class AccessToken(models.Model):
    hashed_email = models.CharField(max_length=64, unique=True)
    access_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def hash_email(cls, email):
        return hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'),
                        bytes(email, 'utf-8'),
                        digestmod=hashlib.sha256).hexdigest()

    @classmethod
    def save_access_token(cls, email, access_token):
        hashed_email = cls.hash_email(email)
        token, _ = cls.objects.get_or_create(hashed_email=hashed_email, defaults={"access_token": access_token})
        token.access_token = access_token
        token.save()
