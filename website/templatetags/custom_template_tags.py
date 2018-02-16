from django import template

register = template.Library()

@register.filter(name="to_currency")
def to_currency(value):
    return '£{:,.2f}'.format(value)
