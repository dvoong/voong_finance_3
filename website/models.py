import datetime
import pandas as pd
import numpy as np
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

import datetime as dt

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
    frequency = models.CharField(max_length=7, null=True)
    end_date = models.DateField(null=True)

    def generate_next_transaction(self, end):

        if self.start_date > end:
            return
        
        if self.previous_transaction_date is None:
            self.previous_transaction_date = self.start_date
            self.save()
            yield Transaction(date=self.start_date,
                              size=self.size,
                              description=self.description,
                              user=self.user,
                              index=len(Transaction.objects.filter(
                                  user=self.user,
                                  date=self.start_date)),
                              repeat_transaction=self)

        f = {
            'daily': add_1day,
            'weekly': add_7days,
            'monthly': next_month,
            'annually': next_year
        }[self.frequency]

        date = f(self.previous_transaction_date)
        t = Transaction(date=date,
                        size=self.size,
                        description=self.description,
                        user=self.user,
                        index=len(Transaction.objects.filter(
                            user=self.user,
                            date=date)),
                        repeat_transaction=self)

        while t.date <= end and (self.end_date is None or t.date <= self.end_date):
            self.previous_transaction_date = t.date
            self.save()
            yield t
            date = f(self.previous_transaction_date)
            t = Transaction(date=date,
                            size=self.size,
                            description=self.description,
                            user=self.user,
                            index=len(Transaction.objects.filter(user=self.user, date=date)),
                            repeat_transaction=self)

    def generate_transactions(self, start, end):

        try:
            last_transaction = Transaction.objects.filter(
                user=self.user,
                date__lte=start
            ).latest('date', 'index')
            closing_balance = last_transaction.closing_balance
        except Transaction.DoesNotExist:
            closing_balance = 0

        date = start

        while date <= end:
            t = Transaction.objects.create(
                date=date,
                size=self.size,
                user=self.user,
                index=len(Transaction.objects.filter(user=self.user, date=date)),
                description=self.description,
                repeat_transaction=self
            )
            if date == start:
                t.closing_balance = closing_balance + self.size
                closing_balance += self.size
            t.save()
            date = self.next_date(date)

        for t in Transaction.objects.filter(date__gt=start).order_by('date', 'index'):
            closing_balance = closing_balance + t.size
            t.closing_balance = closing_balance
            t.save()
            
    def next_date(self, date):
        f = {
            'daily': add_1day,
            'weekly': add_7days,
            'monthly': next_month,
            'annually': next_year
        }[self.frequency]
        date = f(date)
        return date
            
# Create your models here.
class Transaction(models.Model):
    
    date = models.DateField()
    size = models.FloatField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    closing_balance = models.FloatField(null=True)
    index = models.IntegerField()
    repeat_transaction = models.ForeignKey(RepeatTransaction,
                                           null=True,
                                           on_delete=models.CASCADE)

    def recalculate_closing_balances(self):

        Transaction = self.__class__
        
        try:
            last_transaction = Transaction.objects.filter(
                user=self.user,
                date__lte=self.date
            ).latest('date', 'index')
            closing_balance = last_transaction.closing_balance + self.size
        except Transaction.DoesNotExist:
            closing_balance = self.size

        self.closing_balance = closing_balance
        self.save()
            
        # update future transactions
        transactions = Transaction.objects.filter(
            date__gt=self.date,
            user=self.user
        ).order_by('date', 'index')
        for t in transactions:
            # t.closing_balance += self.size
            t.closing_balance = closing_balance + t.size
            closing_balance += t.size
            t.save()

    def get_previous_transaction(self):

        try:
            last_transaction = Transaction.objects.filter(
                Q(date__lt=self.date) | Q(date=self.date, index__lt=self.index),
                user=self.user
            ).latest('date', 'index')
            return last_transaction
        except Transaction.DoesNotExist:
            return None

    def get_later_transactions(self):

        return Transaction.objects.filter(
            Q(date__gt=self.date) | Q(date=self.date, index__gt=self.index),
            user=self.user
        )

    def __str__(self):
        return str(
            (
                ('date', self.date),
                ('index', self.index),
                ('size', self.size),
                ('balance', self.closing_balance),
                ('description', self.description),
            )
        )

def get_transactions(user, start, end):
    return Transaction.objects.filter(user=user,
                                      date__gte=start,
                                      date__lte=end).order_by('date', 'index')
                               
def get_balances(user, start, end):

    repeat_transactions = RepeatTransaction.objects.filter(user=user,
                                                           start_date__lte=end)
        
    for rt in repeat_transactions:
        for t in rt.generate_next_transaction(end):
            t.recalculate_closing_balances()

    dates = pd.DataFrame(pd.date_range(start, end), columns=['date'])
    balances = dates

    try:
        last_transaction = Transaction.objects.filter(
            user=user,
            date__lt=start).latest(
                'date',
                'index')
        closing_balance = last_transaction.closing_balance
    except Transaction.DoesNotExist:
        closing_balance = 0
    
    balances['balance'] = closing_balance

    transactions = get_transactions(user, start, end)
    
    transactions_df = pd.DataFrame(list(transactions.values()))
    if len(transactions):
        transactions_df['date'] = transactions_df['date'].astype('datetime64[ns]')
        transactions_by_date = transactions_df.groupby('date')['size'].sum().reset_index()
        transactions_by_date = dates.merge(transactions_by_date, on='date', how='left').fillna(0)
        transactions_by_date['cumsum']  = transactions_by_date['size'].cumsum()
        balances['balance'] += transactions_by_date['cumsum']
        

    return balances, transactions_df

def add_1day(date):
    return date + datetime.timedelta(days=1)

def add_7days(date):
    return date + datetime.timedelta(days=7)

def next_month(date):
    day = date.day
    if date.month == 12:
        year = date.year + 1
        month = 1
    else:
        year = date.year
        month = date.month + 1

    try:
        next_month = datetime.date(year, month, day)
    except ValueError:
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        next_month = datetime.date(year, month, 1) - datetime.timedelta(days=1)
    return next_month
        
def next_year(date):
    day = date.day
    month = date.month
    year = date.year + 1
    
    try:
        next_year = datetime.date(year, month, day)
    except ValueError:
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        next_year = datetime.date(year, month, 1) - datetime.timedelta(days=1)

    return next_year
    
    
