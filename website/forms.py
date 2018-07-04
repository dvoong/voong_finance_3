import datetime
from django.forms import Form, DateField, CharField, FloatField, IntegerField, BooleanField, ChoiceField, HiddenInput
from django import forms

class DateInput(forms.DateInput):
    input_type = 'date'
    
class NewTransactionForm(Form):

    FREQUENCY_CHOICES = [(1, 'daily'), (2, 'weekly'), (3, 'monthly'), (4, 'yearly')]
    ENDS_HOW_CHOICES = [(1, 'end_date'), (2, 'never'), (3, 'n_transactions')]

    date = DateField(
        initial=datetime.date.today,
        widget=DateInput(
            attrs={
                'id': 'date-input',
            }
        )
    )
    transaction_size = FloatField(widget=forms.NumberInput(attrs={'id': 'transaction-size-input'}))
    description = CharField(widget=forms.TextInput(attrs={'id': 'description-input'}))
    repeats = BooleanField(initial=False, required=False, widget=forms.CheckboxInput(attrs={
        'id': 'repeat-checkbox'
    }))
    frequency = ChoiceField(choices=FREQUENCY_CHOICES, required=False, widget=HiddenInput())
    end_date = DateField(required=False, widget=HiddenInput())
    ends_how = ChoiceField(choices=ENDS_HOW_CHOICES, required=False, widget=HiddenInput())
    n_transactions = IntegerField(required=False, widget=HiddenInput())
    
