from django.db import models

class CustomStrategy(models.Model):
    hashed_email = models.CharField(max_length=128)
    strategies = models.JSONField(default=list)
    method = models.CharField(max_length=128)
    public = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)