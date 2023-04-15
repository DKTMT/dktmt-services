from django.db import models

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('pause', 'Pause'),
        ('close', 'Close'),
    ]
    task_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    duration = models.CharField(max_length=10)
    period = models.CharField(max_length=10)
    symbol = models.CharField(max_length=20)
    timeframe = models.CharField(max_length=10)
    exchange = models.CharField(max_length=20)
    strategies = models.JSONField()
    status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='open')
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'created_by'], name='unique_name_created_by')
        ]