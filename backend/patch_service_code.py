import re

with open('/app/booking/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r"code = models\.CharField\(max_length=50, unique=True, null=True, blank=True, verbose_name='Mã dịch vụ'\)",
    "code = models.CharField(max_length=50, null=True, blank=True, verbose_name='Mã dịch vụ')",
    text
)
# Just in case the order of attributes is different:
text = re.sub(
    r"code = models\.CharField\(([^)]*?)\bunique=True\b([^)]*?)\)",
    r"code = models.CharField(\1\2)",
    text
)
text = text.replace(", ,", ",").replace("(, ", "(")

with open('/app/booking/models.py', 'w', encoding='utf-8') as f:
    f.write(text)