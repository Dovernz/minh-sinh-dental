from django.contrib import admin
from .models import MarketingArticle

@admin.register(MarketingArticle)
class MarketingArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'user', 'created_on')
    search_fields = ('title', 'slug')
    list_filter = ('created_on',)
    prepopulated_fields = {'slug': ('title',)}

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Marketing').exists()
