from django import template
from django.urls import reverse


register = template.Library()


@register.filter
def as_columns(form_field):
    return f'<span class="td first">{form_field.label}</span><span class="td second">{form_field}</span>'


@register.filter
def extras_form_action(form):
    if form.instance.id:
        return reverse('process_existing_extras_form', kwargs={'instance_id': form.instance.id})
    else:
        return reverse('process_new_extras_form', kwargs={'section_id': form.fields['section'].initial.id})


@register.filter
def extras_form_delete(form):
    if form.instance.id:
        action = reverse('delete_extras', kwargs={'instance_id': form.instance.id})
        return f'<button data-action="{action}" class="td delete">X</button>'
    else:
        return ''
