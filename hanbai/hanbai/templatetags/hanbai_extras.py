from django import template


register = template.Library()


@register.filter
def as_columns(form_field):
    return f'<td>{form_field.label}</td><td>{form_field}</td>'
