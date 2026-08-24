import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

inline_old = '''class BookingDetailInline(admin.TabularInline):
    model = BookingDetail
    extra = 1
    fields = ('service_detail', 'actual_price')'''

inline_new = '''from django import forms

class BookingDetailInlineForm(forms.ModelForm):
    class Meta:
        model = BookingDetail
        fields = '__all__'
        widgets = {
            'actual_price': forms.TextInput(attrs={'class': 'formatted-price', 'type': 'text'}),
        }

class BookingDetailInline(admin.TabularInline):
    model = BookingDetail
    form = BookingDetailInlineForm
    extra = 1
    fields = ('service_detail', 'doctor', 'actual_price')'''

text = text.replace(inline_old, inline_new)

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)