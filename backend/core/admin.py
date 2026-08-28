from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from unfold.admin import ModelAdmin # Import Unfold ModelAdmin
from .forms import CustomGroupAdminForm

admin.site.unregister(Group)

@admin.register(Group)
class CustomGroupAdmin(ModelAdmin, GroupAdmin): # Kế thừa cả Unfold và GroupAdmin
    form = CustomGroupAdminForm
