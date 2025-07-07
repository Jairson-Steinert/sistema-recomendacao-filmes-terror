"""
Template tags personalizadas para o sistema de filmes
"""
from django import template

register = template.Library()

@register.filter
def split(value, separator):
    """Divide uma string usando o separador especificado"""
    if value:
        return value.split(separator)
    return []

@register.filter  
def mul(value, arg):
    """Multiplica dois valores"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
