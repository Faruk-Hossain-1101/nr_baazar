from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def add(value, arg):
    """Adds two decimal or numeric values."""
    try:
        return Decimal(value) + Decimal(arg)
    except (ValueError, TypeError):
        return value  # Return the original value if conversion fails

@register.filter
def sub(value, arg):
    """Adds two decimal or numeric values."""
    try:
        return Decimal(value) - Decimal(arg)
    except (ValueError, TypeError):
        return value  # Return the original value if conversion fails
