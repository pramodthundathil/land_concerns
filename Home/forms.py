from django import forms 
from .models import *
from django_ckeditor_5.widgets import CKEditor5Widget


class PictureSlidsForm(forms.ModelForm):
    class Meta:
        model = PictureSlids
        fields = ['pictures', 'sub_image', 'caption', 'sub_headding', 'linked_property', 'show_view_button']
        widgets = {
            'pictures': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'sub_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter caption'}),
            'sub_headding': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subheading'}),
            'linked_property': forms.Select(attrs={'class': 'form-control'}),
            'show_view_button': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BlogForm(forms.ModelForm):
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["body"].required = False

      class Meta:
          model = Blog
          fields = ("blogtitle", "image","description","body")
          widgets = {
              "body": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="default"
              )
          }

class MenusForm(forms.ModelForm):
    class Meta:
        model = Menus
        fields = ['name', 'code', 'menu_position', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Menu Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Menu Code'}),
            'menu_position': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MenuItemsForm(forms.ModelForm):
    class Meta:
        model = MenuItems
        fields = ['title', 'url', 'pages', 'project', 'service', 'menu_type', 'target_blank'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Title'}),
            'url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Custom URL'}),
            'pages': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'menu_type': forms.HiddenInput(), # Likely set automatically or via logic
            'target_blank': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PagesForm(forms.ModelForm):
    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Inactive'),
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    media_lib = forms.ModelChoiceField(
        queryset=MediaLibrary.objects.filter(deleted_at__isnull=True),
        required=False,
        widget=forms.HiddenInput(),
    )
    
    video = forms.ModelChoiceField(
        queryset=MediaLibrary.objects.filter(deleted_at__isnull=True, media_type='video'),
        required=False,
        widget=forms.HiddenInput()
    )
    
    gallery_images = forms.ModelMultipleChoiceField(
        queryset=MediaLibrary.objects.filter(deleted_at__isnull=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'display:none;'}) # Hidden, controlled by JS
    )
    
    gallery_videos = forms.ModelMultipleChoiceField(
        queryset=MediaLibrary.objects.filter(deleted_at__isnull=True, media_type='video'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'display:none;'}) # Hidden, controlled by JS
    )

    page_type = forms.ChoiceField(
        choices=Pages.PAGE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    custom_css = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter custom CSS here...'})
    )

    extra_data = forms.CharField(
        required=False,
        widget=forms.HiddenInput() # We will manage this JSON via JS
    )
    
    parent_id = forms.ModelChoiceField(
        queryset=Pages.objects.filter(deleted_at__isnull=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="No Parent (Top Level)"
    )
    
    class Meta:
        model = Pages
        fields = [
            'code', 'title', 'browser_title', 'description',
            'meta_description', 'meta_keywords', 'media_lib', 'video',
            'status', 'apply_button_top', 'apply_button_bottom', 'parent_id',
            'page_type', 'custom_css', 'extra_data', 'gallery_images', 'gallery_videos'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique code (e.g., about-us)'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter page title'
            }),
            'browser_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter browser title (SEO)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter meta description (SEO)'
            }),
            'meta_keywords': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter keywords separated by commas'
            }),
            'apply_button_top': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'apply_button_bottom': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
    def clean_code(self):
        code = self.cleaned_data.get('code')
        existing = Pages.objects.filter(code=code, deleted_at__isnull=True)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError('This code already exists. Please use a unique code.')
        return code

    def clean_extra_data(self):
        data = self.cleaned_data.get('extra_data')
        if not data:
            return {}
        import json
        try:
            return json.loads(data)
        except:
            return {}

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.media = self.cleaned_data.get('media_lib')
        instance.video = self.cleaned_data.get('video')
        # page_type and custom_css are regular fields, so they are set automatically by super().save(commit=False) if in Meta
        
        if commit:
            instance.save()
            self.save_m2m() # Important for saving gallery_images usage if we weren't doing manual save in view
        return instance

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ProjectsForm(forms.ModelForm):
    project_description = forms.CharField(widget=CKEditor5Widget(config_name='default'))
    primary_image = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    extra_images = MultipleFileField(
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        required=False,
        label="Upload Gallery Images"
    )
    
    media_lib = forms.ModelChoiceField(
        queryset=MediaLibrary.objects.filter(deleted_at__isnull=True),
        required=False,
        widget=forms.HiddenInput(),
        label="Primary Image"
    )
    
    gallery_images = forms.ModelMultipleChoiceField(
        queryset=MediaLibrary.objects.filter(deleted_at__isnull=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'display:none;'})
    )

    class Meta:
        model = Projects
        fields = [
            'project_title', 'project_subname', 'project_description', 
            'project_category', 'is_featured_product',
            'price', 'purpose', 'primary_image', 'gallery_images', 'media_lib', 'icon', 'order'
        ]
        widgets = {
            'project_title': forms.TextInput(attrs={'class': 'form-control'}),
            'project_subname': forms.TextInput(attrs={'class': 'form-control'}),
            'project_category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price (e.g. Lakhs for Sale, Thousands for Rent)'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'is_featured_product': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'icon': forms.HiddenInput(),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Order'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # 1. Determine the primary image to save
        if 'primary_image' in self.files:
            # Direct file upload takes highest priority
            direct_image = self.cleaned_data.get('primary_image')
            if direct_image:
                instance.primary_image = direct_image
        else:
            # If no direct file is uploaded, check if selected from Media Library
            media_item = self.cleaned_data.get('media_lib')
            if media_item:
                instance.primary_image = media_item.file_path
                
        # 2. Save instance and gallery uploads
        if commit:
            instance.save()
            self.save_m2m()
            
            # Save directly uploaded gallery images
            extra_pics = self.files.getlist('extra_images')
            for pic in extra_pics:
                ProjectPictures.objects.create(project=instance, image=pic)
        else:
            # When commit=False, override save_m2m to handle direct gallery uploads
            original_save_m2m = self.save_m2m
            def custom_save_m2m():
                original_save_m2m()
                extra_pics = self.files.getlist('extra_images')
                for pic in extra_pics:
                    ProjectPictures.objects.create(project=instance, image=pic)
            self.save_m2m = custom_save_m2m
            
        return instance


class ServicesForm(forms.ModelForm):
    # Similar to ProjectsForm, allow selecting image from MediaLibrary
    media_lib = forms.ModelChoiceField(
        queryset=MediaLibrary.objects.filter(deleted_at__isnull=True),
        required=False,
        widget=forms.HiddenInput(),
        label="Service Image"
    )

    description = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = Services
        fields = ['title', 'description', 'media_lib', 'icon', 'order'] # image is handled via media_lib
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.HiddenInput(),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Order'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle Image from Media Library Selection
        media_item = self.cleaned_data.get('media_lib')
        if media_item:
            instance.image = media_item.file_path
        
        if commit:
            instance.save()
        return instance


