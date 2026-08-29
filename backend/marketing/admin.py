from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from django.db import models
from .models import MarketingArticle
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import mammoth
import uuid
from django.utils.html import format_html
from django.core.signing import TimestampSigner

def image_handler(image):
    image_data = image.open()
    ext = image.content_type.split('/')[-1] if '/' in image.content_type else 'png'
    filename = f"mammoth_{uuid.uuid4().hex}.{ext}"
    saved_path = default_storage.save(filename, ContentFile(image_data.read()))
    url = default_storage.url(saved_path)
    return {"src": url}

from django import forms

class MarketingArticleForm(forms.ModelForm):
    class Meta:
        model = MarketingArticle
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        word_file = cleaned_data.get('word_file')
        
        if not content and not word_file:
            self.add_error('content', 'Bạn phải nhập nội dung hoặc tải lên một file Word.')
            
        return cleaned_data

@admin.register(MarketingArticle)
class MarketingArticleAdmin(ModelAdmin):
    class Media:
        js = ('js/parse_docx.js',)

    form = MarketingArticleForm
    list_display = ('title', 'slug', 'status', 'user', 'created_on', 'preview_link')
    search_fields = ('title', 'slug', 'focus_keyword')
    list_filter = ('status', 'created_on')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('preview_link',)
    
    fieldsets = (
        ('Nội dung bài viết', {
            'fields': ('title', 'slug', 'status', 'thumbnail_url', 'word_file', 'content', 'user', 'preview_link')
        }),
        ('Cấu hình SEO', {
            'fields': ('meta_title', 'meta_description', 'focus_keyword'),
            'classes': ('collapse',)
        }),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = CKEditorUploadingWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def preview_link(self, obj):
        if obj.pk:
            signer = TimestampSigner()
            token = signer.sign(str(obj.pk))
            url = f"/preview/?token={token}"
            return format_html('<a class="button" href="{}" target="_blank">Xem trước (Preview)</a>', url)
        return "Lưu bài viết trước khi xem trước."
    preview_link.short_description = "Preview"

    def save_model(self, request, obj, form, change):
        if obj.word_file:
            with obj.word_file.open("rb") as docx_file:
                result = mammoth.convert_to_html(
                    docx_file, 
                    convert_image=mammoth.images.inline(image_handler)
                )
                obj.content = result.value
            
            # Delete word file after parsing
            obj.word_file.delete(save=False)
            obj.word_file = None
            
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name='Marketing').exists()

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name='Marketing').exists()

    def has_add_permission(self, request):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name='Marketing').exists()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name='Marketing').exists()

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name='Marketing').exists()
