from django import forms

from . import models


class CustomFieldsFormSet(forms.BaseFormSet):
    def __init__(self, *args, section, initial_instances, **kwargs):
        self.section = section
        initial = []
        for instance in initial_instances:
            initial_values = {'section': section}
            for field in ['field_name', 'value_type', 'string_value', 'integer_value']:
                field_value = getattr(instance, field)
                if field_value:
                    initial_values[field] = field_value

            if instance.field_type == models.ExtraField.FieldTypeChoices.STRING:
                initial_values['type_agnostisc_value'] = instance.string_value
            elif instance.field_type == models.ExtraField.FieldTypeChoices.INTEGER:
                initial_values['type_agnostisc_value'] = str(instance.int_value)
            initial.append(initial_values)

        super().__init__(*args, initial=initial, **kwargs)

    @classmethod
    def build_formset(cls, section, initial_instances):
        Factory = forms.formset_factory(
            CustomFieldForm,
            formset=cls,
            can_delete=True,
            extra=1,
        )
        return Factory(section=section, initial_instances=initial_instances)


class CustomFieldForm(forms.ModelForm):
    type_agnostic_value = forms.CharField(max_length=255)

    def clean(self):
        cleaned_data = super().clean()
        agnostic_value = cleaned_data['type_agnostic_value']

        if cleaned_data['value_type'] == models.ExtraField.FieldTypeChoices.STRING:
            cleaned_data['string_value'] = agnostic_value
            cleaned_data['integer_value'] = None

        elif cleaned_data['value_type'] == models.ExtraField.FieldTypeChoices.INTEGER:
            try:
                int_value = int(agnostic_value)
                cleaned_data['integer_value'] = int_value
                cleaned_data['string_value'] = None
            except TypeError:
                raise forms.ValidationError('数値を入れてください')
        else:
            raise forms.ValidationError('文字又は数値を選んでください')

        return cleaned_data

    class Meta:
        fields = '__all__'
        model = models.ExtraField


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
