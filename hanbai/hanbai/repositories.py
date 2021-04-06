from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404


class OrderRepository:
    def __init__(self,
                 order_model,
                 previous_vehicle_info_model,
                 vehicle_info_model,
                 customer_info_model,
                 registered_holder_info_model,
                 itemization_model,
                 custom_section_model,
                 insurance_tax_model,
                 consumption_tax_model,
                 tax_exemption_model,
                 payment_details_model):
        self.order_model = order_model
        self.previous_vehicle_info_model = previous_vehicle_info_model
        self.vehicle_info_model = vehicle_info_model
        self.customer_info_model = customer_info_model
        self.registered_holder_info_model = registered_holder_info_model
        self.itemization_model = itemization_model
        self.custom_section_model = custom_section_model
        self.insurance_tax_model = insurance_tax_model
        self.consumption_tax_model = consumption_tax_model
        self.tax_exemption_model = tax_exemption_model
        self.payment_details_model = payment_details_model

    def get_in_progress_order(self):
        try:
            self.order_model.objects.filter(
                completed__isnull=True,
            ).latest('last_edited')
        except self.order_model.DoesNotExist:
            return None

    def get_all_orders(self):
        orders = self.order_model.objects.all()
        return orders.order_by('last_edited', '-completed')

    def get_order_or_404(self, order_id):
        return get_object_or_404(self.order_model, pk=order_id)

    @transaction.atomic()
    def initialize_new_order(self):
        previous_vehicle_info = self.previous_vehicle_info_model.objects.create()
        vehicle_info = self.vehicle_info_model.objects.create()
        customer_info = self.customer_info_model.objects.create()
        registered_holder_info = self.registered_holder_info_model.objects.create()
        payment_details = self.payment_details_model.objects.create()
        itemization = self.initialize_itemization()
        return self.order_model.objects.create(
            started=timezone.now(),
            vehicle_info=vehicle_info,
            previous_vehicle_info=previous_vehicle_info,
            customer_info=customer_info,
            registered_holder_info=registered_holder_info,
            itemization=itemization,
            payment_details=payment_details,
        )

    def initialize_itemization(self):
        accessories = self.custom_section_model.objects.create()
        custom_specs = self.custom_section_model.objects.create()
        insurance_tax = self.insurance_tax_model.objects.create()
        consumption_tax = self.consumption_tax_model.objects.create(extras=self.custom_section_model.objects.create())
        consumption_tax_exemption = self.tax_exemption_model.objects.create()
        return self.itemization_model.objects.create(
            accessories=accessories,
            custom_specs=custom_specs,
            insurance_tax=insurance_tax,
            consumption_tax=consumption_tax,
            consumption_tax_exemption=consumption_tax_exemption,
        )


class ExtrasRespository:
    def __init__(self, extra_field_model, extra_section_model, order_model):
        self.extra_field_model = extra_field_model
        self.extra_section_model = extra_section_model
        self.order_model = order_model

    def get_section_or_404(self, section_id):
        return get_object_or_404(self.extra_section_model, pk=section_id)

    def get_field_or_404(self, field_id):
        return get_object_or_404(self.extra_field_model, pk=field_id)

    def get_order_from_section(self, section_id):
        return get_object_or_404(
            self.order_model,
            Q(itemization__consumption_tax__extras=section_id)
            | Q(itemization__accessorie=section_id)
            | Q(itemization__custom_specs=section_id),
        )

    def delete_extra(self, field_id):
        self.extra_field_model.objects.filter(id=field_id).delete()
