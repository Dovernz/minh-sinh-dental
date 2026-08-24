import re
with open(/app/booking/admin.py, r, encoding=utf-8) as f:
    text = f.read()

replacement = "
    def before_import_row(self, row, **kwargs):
        import pandas as pd
        code_val = row.get(code)
        if code_val == "
