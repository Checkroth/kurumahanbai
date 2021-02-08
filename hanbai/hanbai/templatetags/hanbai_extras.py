from django import template


register = template.Library()


@register.filter
def as_columns(form_field):
    return f'<span class="td">{form_field.label}</span><span class="td">{form_field}</span>'
