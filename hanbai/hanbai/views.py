from http import HTTPStatus

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404, FileResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.utils import timezone

from . import api
from . import forms
from .reports import OrderReport
from .constants import FORM_MAPPING


def top(request):
    order_repo = api.get_order_repository()
    in_progress_order = order_repo.get_in_progress_order()
    if in_progress_order:
        return redirect('edit_order')

    else:
        return redirect('order_list')


def edit_order(request, order_id):
    repo = api.get_order_repository()
    order = repo.get_order_or_404(order_id)
    # TODO:: A single form for "extra section"s that handles the input type etc.
    consumption_tax_extras_form = forms.CustomFieldsFormSet.build_formset(
        order.itemization.consumption_tax.extras,
        order.itemization.consumption_tax.extras.fields.all(),
        extra=1,
    )
    accessories_form = forms.CustomFieldsFormSet.build_formset(
        order.itemization.accessories,
        order.itemization.accessories.fields.all(),
        extra=max(1, 10 - order.itemization.accessories.fields.count()),
    )
    custom_specs_form = forms.CustomFieldsFormSet.build_formset(
        order.itemization.custom_specs,
        order.itemization.custom_specs.fields.all(),
        extra=max(1, 5 - order.itemization.custom_specs.fields.count()),
    )

    ctx = {
        'order': order.json(),
        'vehicle_info_form': forms.VehicleInfoForm(instance=order.vehicle_info),
        'previous_vehicle_form': forms.PreviousVehicleInfoForm(instance=order.previous_vehicle_info, prefix='previous'),
        'customer_info_form': forms.CustomerInfoForm(instance=order.customer_info),
        'registered_holder_info_form': forms.RegisteredHolderInfoForm(instance=order.registered_holder_info, prefix='register'),
        'itemization_form': forms.ItemizationForm(instance=order.itemization),
        'insurance_tax_form': forms.InsuranceTaxForm(instance=order.itemization.insurance_tax),
        'consumption_tax_form': forms.ConsumptionTaxForm(instance=order.itemization.consumption_tax),
        'consumption_tax_extras_form': consumption_tax_extras_form,
        'tax_exemption_form': forms.TaxExemptionForm(instance=order.itemization.consumption_tax_exemption),
        'accessories_form': accessories_form,
        'custom_specs_form': custom_specs_form,
    }
    return render(request, 'mainform.html', ctx)


def create_new_order(request):
    repo = api.get_order_repository()
    order = repo.initialize_new_order()
    return redirect('edit_order', order_id=order.pk)


def order_list(request):
    repo = api.get_order_repository()
    orders = repo.get_all_orders()
    return render(request, 'order_list.html', {'orders': orders})


@require_http_methods(['POST'])
def set_form_generic(request, form_class, instance_id):
    form = FORM_MAPPING.get(form_class)
    if not form:
        raise Http404('フォーム種類は存在しません。')
    instance = get_object_or_404(form._meta.model, pk=instance_id)
    form = form(request.POST, instance=instance)
    if form.is_valid():
        form.save()
    else:
        return JsonResponse(form.errors, status=HTTPStatus.BAD_REQUEST)

    return JsonResponse({})


@require_http_methods(['POST'])
def process_existing_extras_form(request, instance_id):
    repo = api.get_extras_repo()
    existing_field = repo.get_field_or_404(instance_id)
    order = repo.get_order_from_section(existing_field.section)
    form_data = request.POST.copy()
    prefix = form_data.pop('form_prefix')[0]
    form_data[f'{prefix}-section'] = existing_field.section
    form = forms.CustomFieldForm(
        form_data,
        instance=existing_field,
        section=existing_field.section,
        prefix=prefix,
    )
    if form.is_valid():
        form.save()
    else:
        return JsonResponse(form.errors, status=HTTPStatus.BAD_REQUEST)
    return JsonResponse({'order': order.json()})


@require_http_methods(['POST'])
def process_new_extras_form(request, section_id):
    repo = api.get_extras_repo()
    order = repo.get_order_from_section(section_id)
    section = repo.get_section_or_404(section_id)
    form_data = request.POST.copy()
    prefix = form_data.pop('form_prefix')[0]
    form_data[f'{prefix}-section'] = section
    form = forms.CustomFieldForm(form_data, section=section, prefix=prefix)
    update_action = None

    if form.is_valid():
        if form.cleaned_data['field_name'] or form.cleaned_data['type_agnostic_value']:
            form.save()
            update_action = reverse(
                'process_existing_extras_form',
                kwargs={'instance_id': form.instance.id},
            )

    else:
        return JsonResponse(form.errors, status=HTTPStatus.BAD_REQUEST)

    return JsonResponse({'new_action': update_action, 'order': order.json()})


@require_http_methods(['DELETE'])
def delete_extra_field(request, instance_id):
    repo = api.get_extras_repo()
    repo.delete_extra(instance_id)
    return JsonResponse({})
    

@require_http_methods(['GET'])
def download_report(request, order_id):
    repo = api.get_order_repository()
    order = repo.get_order_or_404(order_id)
    report = OrderReport(order)
    attachment = report.make_report()
    return FileResponse(attachment, as_attachment=True, filename=f'{order.id}-{timezone.now().date()}.pdf')


@require_http_methods(['GET'])
def get_order(request, order_id):
    repo = api.get_order_repository()
    order = repo.get_order_or_404(order_id)
    return JsonResponse({'order': order.json()})
