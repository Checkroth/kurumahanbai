from django import forms

from . import models


class SelfCleaningForm(forms.ModelForm):
    @property
    def form_class(self):
        raise NotImplementedError()


class CustomFieldsFormSet(forms.BaseModelFormSet):
    @classmethod
    def build_formset(cls, section, initial_instances, extra=1):
        Factory = forms.modelformset_factory(
            models.ExtraField,
            formset=cls,
            can_delete=True,
            form=CustomFieldForm,
            extra=extra,
            fields='__all__',
        )

        return Factory(
            prefix=type(section).__name__,
            form_kwargs={'section': section},
            queryset=initial_instances,
        )


class CustomFieldForm(SelfCleaningForm):
    form_class = 'custom_field'
    type_agnostic_value = forms.CharField(max_length=255, required=False)
    def __init__(self, *args, section, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section'].initial = section
        self.fields['value_type'].required = False
        self.fields['value_type'].choices = [models.ExtraField.FieldTypeChoices.INTEGER,
                                             models.ExtraField.FieldTypeChoices.STRING]
        self.fields['type_agnostic_value'].initial = (self.instance.string_value or
                                                      self.instance.integer_value)

    def clean(self):
        cleaned_data = super().clean()
        agnostic_value = cleaned_data.get('type_agnostic_value')
        if not agnostic_value:
            return cleaned_data

        try:
            int_value = int(agnostic_value)
            cleaned_data['integer_value'] = int_value
            cleaned_data['string_value'] = None
            cleaned_data['value_type'] = int(models.ExtraField.FieldTypeChoices.INTEGER)
        except (TypeError, ValueError):
            cleaned_data['integer_value'] = None
            cleaned_data['string_value'] = agnostic_value
            cleaned_data['value_type'] = models.ExtraField.FieldTypeChoices.STRING.name

        return cleaned_data

    class Meta:
        fields = '__all__'
        model = models.ExtraField


class BasicVehicleInfoForm(SelfCleaningForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inspection_year'].widget.attrs['class'] = 'double'
        self.fields['inspection_month'].widget.attrs['class'] = 'double'
        self.fields['model_year'].widget.attrs['class'] = 'double'
        self.fields['model_month'].widget.attrs['class'] = 'double'

    class Meta:
        abstrasct = True


class VehicleInfoForm(BasicVehicleInfoForm):
    form_class = 'vehicle_info'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inspection_year'].widget.attrs['class'] = 'double'
        self.fields['inspection_month'].widget.attrs['class'] = 'double'

    class Meta:
        fields = '__all__'
        model = models.VehicleInfo


class PreviousVehicleInfoForm(BasicVehicleInfoForm):
    form_class = 'previous_vehicle_info'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inspection_year'].widget.attrs['class'] = 'double'
        self.fields['inspection_month'].widget.attrs['class'] = 'double'

    class Meta:
        fields = '__all__'
        model = models.PreviousVehicleInfo


class CustomerInfoForm(SelfCleaningForm):
    form_class = 'customer_info'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_phone'].widget.attrs['class'] = 'double'

    class Meta:
        fields = '__all__'
        model = models.CustomerInfo


class RegisteredHolderInfoForm(SelfCleaningForm):
    form_class = 'registered_holder_info'

    class Meta:
        fields = '__all__'
        model = models.RegisteredHolderInfo


class ItemizationForm(SelfCleaningForm):
    form_class = 'itemization'

    class Meta:
        fields = [
            'vehicle_price',
            'special_discount',
            'down_payment',
            'trade_in_price',
        ]
        model = models.Itemization


class InsuranceTaxForm(SelfCleaningForm):
    form_class = 'insurance_tax'

    class Meta:
        fields = '__all__'
        model = models.InsuranceTax


class ConsumptionTaxForm(SelfCleaningForm):
    form_class = 'consumption_tax'

    class Meta:
        exclude = ['extras']
        model = models.ConsumptionTax


class TaxExemptionForm(SelfCleaningForm):
    form_class = 'tax_exemption'

    class Meta:
        fields = '__all__'
        model = models.TaxExemption
