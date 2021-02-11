from . import forms


FORM_MAPPING = {
    forms.CustomFieldForm.form_class: forms.CustomFieldForm,
    forms.VehicleInfoForm.form_class: forms.VehicleInfoForm,
    forms.PreviousVehicleInfoForm.form_class: forms.PreviousVehicleInfoForm,
    forms.CustomerInfoForm.form_class: forms.CustomerInfoForm,
    forms.RegisteredHolderInfoForm.form_class: forms.RegisteredHolderInfoForm,
    forms.ItemizationForm.form_class: forms.ItemizationForm,
    forms.InsuranceTaxForm.form_class: forms.InsuranceTaxForm,
    forms.ConsumptionTaxForm.form_class: forms.ConsumptionTaxForm,
    forms.TaxExemptionForm.form_class: forms.TaxExemptionForm,
}
