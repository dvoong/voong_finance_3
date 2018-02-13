from django.db import models

# Create your models here.
class Transaction(models.Model):
    
    date = models.DateField()
    size = models.FloatField()
    description = models.TextField()
