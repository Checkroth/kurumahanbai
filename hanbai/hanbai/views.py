from django.shortcuts import render, redirect

from . import api
from . import forms


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
    ctx = {
        'order': order,
        'vehicle_info_form': forms.VehicleInfoForm(instance=order.vehicle_info),
        'previous_vehicle_form': forms.PreviousVehicleInfoForm(instance=order.previous_vehicle_info),
        'customer_info_form': forms.CustomerInfoForm(instance=order.customer_info),
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
