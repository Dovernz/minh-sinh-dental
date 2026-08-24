import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add BookingDetailInline
inline = '''
class BookingDetailInline(admin.TabularInline):
    model = BookingDetail
    extra = 1
    fields = ('service', 'price', 'quantity')
'''

# Find BookingAdmin and inject inline
if 'class BookingDetailInline' not in text:
    text = text.replace('class BookingAdmin(BaseRBACAdmin):', inline + '\nclass BookingAdmin(BaseRBACAdmin):\n    inlines = [BookingDetailInline]')

# Add BillingAdmin with VietQR logic
billing_admin = '''
from booking.models import Billing, TopupInfo
from django.utils.safestring import mark_safe

@admin.register(Billing)
class BillingAdmin(BaseRBACAdmin):
    list_display = ('booking', 'sub_total', 'discount', 'final_total', 'created_on')
    readonly_fields = ('sub_total', 'adjustment', 'final_total', 'payment_qr_code')
    search_fields = ('booking__booking_id', 'booking__customer__full_name')
    
    fieldsets = (
        ('Thông tin chung', {
            'fields': ('booking',)
        }),
        ('Kế toán', {
            'fields': ('sub_total', 'discount', 'manual_total', 'adjustment', 'final_total')
        }),
        ('Thanh toán', {
            'fields': ('payment_qr_code',)
        })
    )

    def payment_qr_code(self, obj):
        if obj.pk and obj.final_total > 0:
            topup = TopupInfo.objects.filter(is_default=True).first()
            if not topup:
                topup = TopupInfo.objects.first()
            if topup:
                # VietQR formula
                bank = topup.bank_name
                account = topup.account_number
                name = topup.account_name.replace(' ', '%20') if topup.account_name else ''
                amount = int(obj.final_total)
                info = f"Thanh toan Booking {obj.booking.booking_id}".replace(' ', '%20')
                url = f"https://img.vietqr.io/image/{bank}-{account}-compact2.png?amount={amount}&addInfo={info}&accountName={name}"
                return mark_safe(f'<img src="{url}" alt="QR Code" style="max-width: 300px;"/>')
        return "Chưa có thông tin hoặc tổng tiền = 0"
    payment_qr_code.short_description = "QR Thanh Toán"
'''

if 'class BillingAdmin' not in text:
    text += '\n' + billing_admin

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)