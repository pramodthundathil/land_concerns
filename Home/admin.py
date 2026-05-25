from django.contrib import admin
from django.utils.html import format_html
from .models import VideoSlide, Projects, MediaLibrary, ProjectPictures, Services, Menus, MenuItems, Pages

admin.site.register(VideoSlide)
admin.site.register(MediaLibrary)

class ProjectPicturesInline(admin.TabularInline):
    model = ProjectPictures
    extra = 3
    fields = ('image', 'image_preview', 'title')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 80px; max-width: 150px; border-radius: 4px;" />', obj.image.url)
        return "No image uploaded yet"
    image_preview.short_description = "Preview"

@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'project_status', 'is_featured_product', 'price', 'purpose')
    filter_horizontal = ('gallery_images',)
    prepopulated_fields = {"slug": ("project_title",)}
    inlines = [ProjectPicturesInline]
    fields = ('project_title', 'slug', 'project_subname', 'project_description', 
              'primary_image', 'primary_image_preview', 'project_category', 'project_status', 
              'is_featured_product', 'price', 'purpose', 'gallery_images', 'order')
    readonly_fields = ('primary_image_preview',)

    def primary_image_preview(self, obj):
        if obj.primary_image:
            return format_html('<img src="{}" style="max-height: 120px; max-width: 250px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.15);" />', obj.primary_image.url)
        return "No primary image uploaded yet"
    primary_image_preview.short_description = "Primary Image Preview"


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview')
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('image_preview',)
    fields = ('title', 'slug', 'description', 'image', 'image_preview', 'order', 'icon')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px; border-radius: 4px;" />', obj.image.url)
        return "No image uploaded"
    image_preview.short_description = "Image Preview"


admin.site.register(Menus)
admin.site.register(MenuItems)
admin.site.register(Pages)
