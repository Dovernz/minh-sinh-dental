from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from django.db import models
from .models import MarketingArticle
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import mammoth
import uuid
from django.utils.safestring import mark_safe
from django.core.signing import TimestampSigner

def image_handler(image):
    image_data = image.open()
    ext = image.content_type.split('/')[-1] if '/' in image.content_type else 'png'
    filename = f"mammoth_{uuid.uuid4().hex}.{ext}"
    saved_path = default_storage.save(filename, ContentFile(image_data.read()))
    url = default_storage.url(saved_path)
    return {"src": url}

from django import forms
from tinymce.widgets import TinyMCE

class MarketingArticleForm(forms.ModelForm):
    class Meta:
        model = MarketingArticle
        fields = '__all__'
        widgets = {
            
        }
        
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


from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

class CustomCloudinaryWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        
        # 1. Nếu có ảnh đã lưu: Hiện ảnh (click để phóng to) và Tên file
        if value and hasattr(value, 'url'):
            # Trích xuất tên file từ Cloudinary ID
            file_name = str(value).split('/')[-1] if value else 'Đã tải lên'
            
            output.append(f'''
                <div style="margin-bottom: 16px; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px dashed #4b5563; width: fit-content;">
                    <a href="{value.url}" target="_blank" style="display: block; cursor: zoom-in; border-radius: 4px; overflow: hidden; margin-bottom: 8px; transition: opacity 0.2s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                        <img src="{value.url}" style="max-height: 200px; display: block;" title="Nhấn để phóng to ảnh" />
                    </a>
                    <div style="font-size: 13px; color: #9ca3af; display: flex; align-items: center; gap: 6px;">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20"><path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"></path></svg>
                        {file_name}
                    </div>
                </div>
            ''')
            
        # 2. Render input chọn file (thêm CSS class để đồng bộ theme Unfold)
        output.append(super().render(name, value, attrs, renderer))
        
        return mark_safe(''.join(output))

class MarketingArticleAdminForm(forms.ModelForm):
    thumbnail = forms.FileField(
        widget=CustomCloudinaryWidget(),
        required=False,
        label="Ảnh Thumbnail (Tải lên)"
    )
    content = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), 
        label="Nội dung",
        required=False
    )

    class Meta:
        model = MarketingArticle
        fields = '__all__'
        widgets = {
        }
        widgets = {
            
        }

@admin.register(MarketingArticle)

class MarketingArticleAdmin(ModelAdmin):
    form = MarketingArticleAdminForm
    class Media:
        js = (
            'js/parse_docx.js',
            'js/preview_cloudinary.js',
            'tinymce/tinymce.min.js',
            'django_tinymce/init_tinymce.js',
        )
    def get_form(self, request, obj=None, **kwargs):
        css_style = """
<style>
    .field-thumbnail input[type="file"] {
        color: transparent;
    }
    .field-thumbnail input[type="file"]::-webkit-file-upload-button {
        visibility: hidden;
    }
    .field-thumbnail input[type="file"]::before {
        content: 'Tải ảnh lên (Upload)';
        display: inline-block;
        background: #1e293b;
        color: white;
        border: 1px solid #999;
        border-radius: 6px;
        padding: 8px 16px;
        outline: none;
        white-space: nowrap;
        cursor: pointer;
        font-weight: 500;
        font-size: 14px;
    }
    .field-thumbnail input[type="file"]:hover::before {
        background: #334155;
    }
</style>
<script src="https://media-library.cloudinary.com/global/all.js"></script>
"""
        from django.utils.safestring import mark_safe
        form = super().get_form(request, obj, **kwargs)
        js_click_image = """
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                setTimeout(function() {
                    let images = document.querySelectorAll('.form-row img');
                    images.forEach(function(img) {
                        img.style.cursor = 'zoom-in';
                        img.title = 'Click để xem kích thước đầy đủ';
                        img.addEventListener('click', function() {
                            window.open(img.src, '_blank');
                        });
                    });
                }, 1000);
            });
        </script>
        """
        if 'title' in form.base_fields:
            if not form.base_fields['title'].help_text:
                form.base_fields['title'].help_text = ''
            form.base_fields['title'].help_text += mark_safe(js_click_image)
        return form


    form = MarketingArticleAdminForm
    list_display = ('title', 'slug', 'status', 'user', 'created_on', 'preview_link')
    search_fields = ('title', 'slug', 'focus_keyword')
    list_filter = ('status', 'created_on')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('preview_link',)
    
    fieldsets = (
        ('Nội dung bài viết', {
            'fields': ('title', 'slug', 'status', 'thumbnail', 'word_file', 'content', 'user', 'preview_link')
        }),
        ('Cấu hình SEO', {
            'fields': ('meta_title', 'meta_description', 'focus_keyword'),
            'classes': ('collapse',)
        }),
    )

    

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
