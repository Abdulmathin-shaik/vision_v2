from django import template

register = template.Library()

@register.filter(name='index')
def index(lst, i):
    try:
        return float(lst[i]) * 100  # Convert to percentage
    except:
        return 0 