import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add imports
if 'from django.shortcuts import get_object_or_404, render' not in text:
    text = text.replace('from django.urls import path', 'from django.urls import path\nfrom django.shortcuts import get_object_or_404, render\nfrom django.utils.html import format_html')

# Update BillingAdmin
billing_methods = '''
    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('<int:billing_id>/print/', self.admin_site.admin_view(self.print_invoice_view), name='billing-print-invoice'),
        ]
        return my_urls + urls

    def print_invoice_view(self, request, billing_id):
        from .models import TopupInfo
        billing = get_object_or_404(Billing, pk=billing_id)
        booking = billing.booking
        details = booking.details.all()
        customer = booking.customer
        
        qr_url = ""
        if billing.final_total > 0:
            topup = TopupInfo.objects.filter(is_default=True).first()
            if not topup:
                topup = TopupInfo.objects.first()
            if topup:
                bank = topup.bank_name
                account = topup.account_number
                name = topup.account_name.replace(' ', '%20') if topup.account_name else ''
                amount = int(billing.final_total)
                info = f"Thanh toan Booking {booking.booking_id}".replace(' ', '%20')
                qr_url = f"https://img.vietqr.io/image/{bank}-{account}-compact2.png?amount={amount}&addInfo={info}&accountName={name}"

        context = {
            'billing': billing,
            'booking': booking,
            'details': details,
            'customer': customer,
            'qr_url': qr_url,
        }
        return render(request, 'admin/booking/billing/invoice.html', context)

    def print_invoice_button(self, obj):
        if obj.pk:
            return format_html('<a href="{}/print/" target="_blank" class="button" style="background-color:#007bff; color:white; padding:5px 10px; border-radius:3px; text-decoration:none;">🖨️ In Hóa Đơn</a>', obj.pk)
        return ""
    print_invoice_button.short_description = "In Hóa Đơn"

'''

text = text.replace("    list_display = ('booking', 'sub_total', 'discount', 'final_total', 'created_on')", "    list_display = ('booking', 'sub_total', 'discount', 'final_total', 'created_on', 'print_invoice_button')")
text = text.replace("    readonly_fields = ('sub_total', 'adjustment', 'final_total', 'payment_qr_code')", "    readonly_fields = ('sub_total', 'adjustment', 'final_total', 'payment_qr_code', 'print_invoice_button')")
text = text.replace("        ('Thanh toán', {\n            'fields': ('payment_qr_code',)\n        })", "        ('Thanh toán', {\n            'fields': ('payment_qr_code', 'print_invoice_button')\n        })")

if 'def print_invoice_button' not in text:
    text = text.replace('    def payment_qr_code(self, obj):', billing_methods + '\n    def payment_qr_code(self, obj):')

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)