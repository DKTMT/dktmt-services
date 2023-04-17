from django.db import models

class CustomStrategy(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
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

class BacktestResult(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('running', 'Running')
    ]
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready')
    last_update = models.DateTimeField(auto_now=True)
    number_of_buy_sell = models.PositiveIntegerField(null=True)
    accuracy_of_buy_sell = models.FloatField(null=True)
    number_of_mock_trade = models.PositiveIntegerField(null=True)
    start_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    final_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return self.name