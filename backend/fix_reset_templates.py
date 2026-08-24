import os

file_path = "core/urls.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "auth_views.PasswordResetView.as_view()": "auth_views.PasswordResetView.as_view(template_name='unfold/password_reset.html')",
    "auth_views.PasswordResetDoneView.as_view()": "auth_views.PasswordResetDoneView.as_view(template_name='unfold/password_reset_done.html')",
    "auth_views.PasswordResetConfirmView.as_view()": "auth_views.PasswordResetConfirmView.as_view(template_name='unfold/password_reset_confirm.html')",
    "auth_views.PasswordResetCompleteView.as_view()": "auth_views.PasswordResetCompleteView.as_view(template_name='unfold/password_reset_complete.html')"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated urls.py with Unfold templates.")
