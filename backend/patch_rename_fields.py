import re

with open('/app/booking/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('service = models.ForeignKey("ServiceDetail", on_delete=models.SET_NULL, null=True)', 'service_detail = models.ForeignKey("ServiceDetail", on_delete=models.SET_NULL, null=True, verbose_name="Dịch vụ")')
text = text.replace('price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Đơn giá")', 'actual_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Đơn giá")')
text = text.replace('if not self.price and self.service:', 'if not self.actual_price and self.service_detail:')
text = text.replace('self.price = self.service.price or 0', 'self.actual_price = self.service_detail.price or 0')
text = text.replace('self.service.name if self.service else', 'self.service_detail.name if self.service_detail else')

# Update Billing.save() calculation
text = text.replace('sum((d.price * d.quantity) for d in details)', 'sum((d.actual_price * d.quantity) for d in details)')

with open('/app/booking/models.py', 'w', encoding='utf-8') as f:
    f.write(text)