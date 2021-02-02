from django import forms

from . import models


class VehicleInfoForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = models.VehicleInfo


class PreviousVehicleInfoForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = models.PreviousVehicleInfo


class CustomerInfoForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = models.CustomerInfo
