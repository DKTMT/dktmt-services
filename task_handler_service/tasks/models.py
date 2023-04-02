from django.db import models

class MyModel(models.Model):
    my_field = models.CharField(max_length=255)
    
    def __str__(self):
        return self.my_field
