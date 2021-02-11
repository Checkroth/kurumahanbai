from django import template
from django.urls import reverse


register = template.Library()


@register.filter
def as_columns(form_field):
    return f'<span class="td">{form_field.label}</span><span class="td">{form_field}</span>'


@register.filter
def extras_form_action(form):
    if form.instance.id:
        return reverse('process_existing_extras_form', kwargs={'instance_id': form.instance.id})
    else:
        return reverse('process_new_extras_form', kwargs={'section_id': form.fields['section'].initial.id})
