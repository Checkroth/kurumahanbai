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
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
    path('', views.top, name='top'),
    path('create_new_order/', views.create_new_order, name='create_new_order'),
    path('edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('order_list/', views.order_list, name='order_list'),
    path('set_form_generic/<int:order_id>/<str:form_class>/<int:instance_id>', views.set_form_generic, name='set_form_generic'),
    path('process_new_extras_form/<int:section_id>', views.process_new_extras_form, name='process_new_extras_form'),
    path('process_extras_form/<int:instance_id>', views.process_existing_extras_form, name='process_existing_extras_form'),
    path('delete_extras/<int:instance_id>', views.delete_extra_field, name='delete_extras'),
    path('download/<int:order_id>', views.download_report, name='download_report'),
    path('delete/<int:order_id>', views.delete_order, name='delete_order'),
]
