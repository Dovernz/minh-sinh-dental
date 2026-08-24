import re

with open('/app/booking/templates/admin/booking/billing/invoice.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace column headers
text = text.replace('<th>SL</th>', '')

# Replace item loop
old_tr = '''            <tr>
                <td>{{ forloop.counter }}</td>
                <td>{{ item.service.name|default:"Dịch vụ khác" }}</td>
                <td>{{ item.price|floatformat:0 }} ₫</td>
                <td>{{ item.quantity }}</td>
            </tr>'''
new_tr = '''            <tr>
                <td>{{ forloop.counter }}</td>
                <td>{{ item.service_detail.name|default:"Dịch vụ khác" }}</td>
                <td>{{ item.actual_price|floatformat:0 }} ₫</td>
            </tr>'''
text = text.replace(old_tr, new_tr)
text = text.replace('colspan="4"', 'colspan="3"')

with open('/app/booking/templates/admin/booking/billing/invoice.html', 'w', encoding='utf-8') as f:
    f.write(text)