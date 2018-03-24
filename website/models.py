import datetime
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Transaction(models.Model):
    
    date = models.DateField()
    size = models.FloatField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    closing_balance = models.FloatField()
    index = models.IntegerField()

class RepeatTransaction(models.Model):

    REPEAT_STATUSES = (
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
    )

    start_date = models.DateField()
    previous_transaction_date = models.DateField(null=True)
    size = models.FloatField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    index = models.IntegerField()
    frequency = models.CharField(max_length=7)

    def generate_next_transaction(self):
        if self.previous_transaction_date is None:
            return Transaction(date=self.start_date,
                               size=self.size,
                               description=self.description,
                               user=self.user)
        else:
            f = {
                'daily': 1,
                'weekly': 7,
                'monthly': 28
            }[self.frequency]
            return Transaction(date=self.previous_transaction_date + datetime.timedelta(days=f),
                            size=self.size,
                            description=self.description,
                            user=self.user)
                               
                               
