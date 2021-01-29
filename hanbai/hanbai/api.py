from . import repositories
from . import models


def get_order_repository():
    return repositories.OrderRepository(
        models.Order,
        models.PreviousVehicleInfo,
        models.VehicleInfo,
        models.CustomerInfo,
        models.RegisteredHolderInfo,
        models.Itemization,
        models.CustomSection,
        models.InsuranceTax,
        models.ConsumptionTax,
        models.TaxExemption,
    )
