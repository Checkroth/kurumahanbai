"""hanbai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.top, name='top'),
    path('create_new_order/', views.create_new_order, name='create_new_order'),
    path('edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('order_list/', views.order_list, name='order_list'),
    path('set_vehicle_info/', views.set_vehicle_info, name='set_vehicle_info'),
    path('set_form_generic/<str:form_class>/<int:instance_id>', views.set_form_generic, name='set_form_generic'),
    path('process_new_extras_form/<int:section_id>', views.process_new_extras_form, name='process_new_extras_form'),
    path('process_extras_form/<int:instance_id>', views.process_existing_extras_form, name='process_existing_extras_form'),
]
