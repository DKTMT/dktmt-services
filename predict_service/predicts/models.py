from django.db import models

class CustomStrategy(models.Model):
    name = models.CharField(max_length=255)
    method = models.JSONField()
    public = models.BooleanField()
    anonymous = models.BooleanField()
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'created_by'], name='unique_name_created_by')
        ]
