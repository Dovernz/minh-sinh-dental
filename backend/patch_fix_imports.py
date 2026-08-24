import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the broken ServiceDetailAdmin.get_urls
broken_block = '''        from django.urls import path
from django.shortcuts import get_object_or_404, render
from django.utils.html import format_html
        my_urls = ['''
fixed_block = '''        from django.urls import path
        my_urls = ['''

text = text.replace(broken_block, fixed_block)

# Add the missing imports at the very top (after coding=utf-8 or first line)
imports = '''
from django.shortcuts import get_object_or_404, render
from django.utils.html import format_html
'''
text = imports + text

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)