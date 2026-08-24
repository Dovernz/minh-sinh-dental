from django.db import models
from booking.models import Discount

class CatalogDiscount(Discount):
    class Meta:
        proxy = True
        app_label = "services_menu"
        verbose_name = "Khuyến mãi"
        verbose_name_plural = "Khuyến mãi"