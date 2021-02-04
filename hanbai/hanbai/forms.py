from django import forms

from . import models


class BasicVehicleInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inspection_year'].widget.attrs['class'] = 'double'
        self.fields['inspection_month'].widget.attrs['class'] = 'double'
        self.fields['model_year'].widget.attrs['class'] = 'double'
        self.fields['model_month'].widget.attrs['class'] = 'double'

    class Meta:
        abstrasct = True


class VehicleInfoForm(BasicVehicleInfoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inspection_year'].widget.attrs['class'] = 'double'
        self.fields['inspection_month'].widget.attrs['class'] = 'double'

    class Meta:
        fields = '__all__'
        model = models.VehicleInfo


class PreviousVehicleInfoForm(BasicVehicleInfoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inspection_year'].widget.attrs['class'] = 'double'
        self.fields['inspection_month'].widget.attrs['class'] = 'double'

    class Meta:
        fields = '__all__'
        model = models.PreviousVehicleInfo


class CustomerInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_phone'].widget.attrs['class'] = 'double'

    class Meta:
        fields = '__all__'
        model = models.CustomerInfo


class RegisteredHolderInfoForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = models.RegisteredHolderInfo


class ItemizationForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = models.Itemization


class InsuranceTaxForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = models.InsuranceTax


class ConsumptionTaxForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = models.ConsumptionTax


class TaxExemptionForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = models.TaxExemption
