from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter
def sum_prices(materials):
    return sum(material['price'] for material in materials)

@register.filter
def replace_underscore(value):
    return value.replace('_', ' ').title()