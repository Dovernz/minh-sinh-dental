import re
models_path = 'backend/booking/models.py'
with open(models_path, 'r', encoding='utf-8') as f: models = f.read()
billing_pattern = r'(class Billing\(models\.Model\):.*?)(?=created_at = models\.DateTimeField)'
status_field = '''status = models.CharField(max_length=20, choices=[('UNPAID', 'Chưa thanh toán'), ('PAID', 'Đã thanh toán')], default='UNPAID', verbose_name="Trạng thái")\n    '''
models = re.sub(billing_pattern, r'\g<1>' + status_field, models, flags=re.DOTALL)
with open(models_path, 'w', encoding='utf-8') as f: f.write(models)
