import re

with open('/app/booking/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Comment out doctor and actual_price in Booking
text = re.sub(r"    doctor = models\.ForeignKey\(Employee, on_delete=models\.SET_NULL, null=True, blank=True, related_name='handled_bookings', verbose_name='Bác sĩ khám'\)\n",
              r"    # doctor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_bookings', verbose_name='Bác sĩ khám')\n", text)
text = re.sub(r"    actual_price = models\.IntegerField\(null=True, blank=True, verbose_name='Số tiền thực tế'\)\n",
              r"    # actual_price = models.IntegerField(null=True, blank=True, verbose_name='Số tiền thực tế')\n", text)

# Add doctor to BookingDetail and change actual_price
old_actual_price_bd = '    actual_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Đơn giá")'
new_actual_price_bd = '''    doctor = models.ForeignKey("Employee", on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'Doctor'}, verbose_name="Bác sĩ khám")
    actual_price = models.IntegerField(null=True, blank=True, verbose_name="Đơn giá")'''
text = text.replace(old_actual_price_bd, new_actual_price_bd)

with open('/app/booking/models.py', 'w', encoding='utf-8') as f:
    f.write(text)