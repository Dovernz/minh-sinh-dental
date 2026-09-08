import re

views_path = 'backend/booking/views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    views = f.read()

confirm_api = '''@method_decorator(csrf_exempt, name='dispatch')
class POSConfirmPaymentAPIView(View):
    def post(self, request):
        try:
            import json
            from django.db.models import Sum
            from booking.models import Billing, Payment
            from django.db import transaction
            
            data = json.loads(request.body)
            pay_amount = float(data.get('amount', 0))
            
            with transaction.atomic():
                billing = Billing.objects.get(billing_id=data.get('billing_id'))
                
                prev_payments = Payment.objects.filter(billing=billing).aggregate(Sum('amount'))['amount__sum'] or 0
                
                total = float(billing.final_total)
                remain = total - float(prev_payments) - pay_amount
                if remain < 0: remain = 0
                
                Payment.objects.create(
                    billing=billing,
                    amount=pay_amount,
                    payment_method=data.get('payment_method', 'CASH'),
                    total_billing=total,
                    amount_remain=remain
                )
                
                billing.status = 'PAID' if remain <= 0 else 'INSTALLMENT'
                billing.save()
                
            return JsonResponse({'status': 'success', 'remain': remain, 'bill_status': billing.status})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
'''

# Safely replace only POSConfirmPaymentAPIView
start_str = "class POSConfirmPaymentAPIView(View):"
start_idx = views.find(start_str)
if start_idx != -1:
    # Find the decorator above it
    decorator_idx = views.rfind("@method_decorator", 0, start_idx)
    # The end is the end of the file or next class
    end_idx = views.find("\nclass ", start_idx)
    if end_idx == -1:
        end_idx = len(views)
        
    views = views[:decorator_idx] + confirm_api + views[end_idx:]

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views)
