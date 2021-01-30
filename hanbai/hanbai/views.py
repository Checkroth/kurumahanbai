from django.shortcuts import render, redirect

from . import api


def top(request):
    order_repo = api.get_order_repository()
    in_progress_order = order_repo.get_in_progress_order()
    if in_progress_order:
        return redirect('edit_order')

    else:
        return redirect('order_list')


def edit_order(request, order_id):
    return render(request, 'mainform.html')


def create_new_order(request):
    repo = api.get_order_repository()
    order = repo.initialize_new_order()
    return redirect('edit_order', order_id=order.pk)


def order_list(request):
    repo = api.get_order_repository()
    orders = repo.get_all_orders()
    return render(request, 'order_list.html', {'orders': orders})
