from django.db import models
from booking.models import ServiceCategory, ServiceDetail

class ServiceCategoryProxy(ServiceCategory):
    class Meta:
        proxy = True
        verbose_name = 'Danh mục dịch vụ'
        verbose_name_plural = 'Danh mục dịch vụ'

class ServiceDetailProxy(ServiceDetail):
    class Meta:
        proxy = True
        verbose_name = 'Chi tiết dịch vụ'
        verbose_name_plural = 'Chi tiết dịch vụ'
