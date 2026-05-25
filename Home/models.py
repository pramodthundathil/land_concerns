from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify



# Create your models here.
class VideoSlide(models.Model):
    video = models.FileField(upload_to='slidevideo')
    caption = models.CharField(max_length=255)
    sub_headding = models.CharField(max_length=255)
    date_updated = models.DateField(auto_now_add=True)


class PictureSlids(models.Model):
    pictures = models.FileField(upload_to='picture')
    sub_image = models.FileField(upload_to="picture/sub_image")
    caption = models.CharField(max_length=255)
    sub_headding = models.CharField(max_length=255)
    linked_property = models.ForeignKey('Projects', on_delete=models.SET_NULL, null=True, blank=True, related_name='slides')
    show_view_button = models.BooleanField(default=False)
    date_updated = models.DateField(auto_now_add=True)

class Job(models.Model):
    title = models.CharField(max_length=255)  # Job Title
    experience = models.CharField(max_length=255)  # Minimum Experience in Years  
    education = models.CharField(max_length=255)  # Education Requirement
    description = models.TextField()  # Job Description
    salary = models.CharField(max_length=100)  # Salary Description
    location = models.CharField(max_length=255)  # Job Location
    posted_on = models.DateField(auto_now_add=True)  # Posting Date
    
    def __str__(self):
        return self.title



class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    position = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    education = models.CharField(max_length=200)
    experience = models.CharField(max_length=200)
    address = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    portfolio = models.FileField(upload_to='portfolios/', blank=True, null=True)  # Portfolio is optional
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Projects(models.Model):
    project_title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    project_subname = models.CharField(max_length=255)
    project_description = CKEditor5Field()
    primary_image = models.FileField(upload_to="project_primary_image")
    project_category = models.CharField(max_length=255, choices=
                                        (
                                            ("House", "House"), 
                                            ("Apartments", "Apartments"), 
                                            ("Land", "Land"), 
                                            ("Commercial", "Commercial"), 
                                            ("Shops", "Shops"),
                                            ("Office Spaces", "Office Spaces"),
                                            ("Other", "Other")
                                        )
                                        )
    project_status = models.CharField(max_length=20, choices=(("On Going","On Going"),("Completed","Completed")))
    is_featured_product = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True, blank=True)
    purpose = models.CharField(max_length=10, choices=(("Sale", "For Sale"), ("Rent", "For Rent")), default="Sale")
    
    # ManyToMany field to MediaLibrary for gallery images
    gallery_images = models.ManyToManyField('MediaLibrary', related_name='project_gallery_images', blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.project_status = "Completed"
        if not self.slug:
            self.slug = slugify(self.project_title)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.project_title)

    @property
    def formatted_price(self):
        if not self.price or self.price == 0:
            return "Price on Request"
        if self.purpose == 'Rent':
            val = int(self.price)
            return f"₹{val:,} / month"
        else:
            val = float(self.price)
            if val >= 10000000:
                cr_val = val / 10000000
                if cr_val.is_integer():
                    return f"₹{int(cr_val)} Crore"
                else:
                    return f"₹{cr_val:.2f} Crores".rstrip('0').rstrip('.')
            else:
                lakh_val = val / 100000
                if lakh_val.is_integer():
                    return f"₹{int(lakh_val)} Lakhs"
                else:
                    return f"₹{lakh_val:.2f} Lakhs".rstrip('0').rstrip('.')
    
    icon = models.CharField(max_length=100, default='bi bi-flower1', blank=True, null=True, help_text="Bootstrap Icon Class")

class ProjectPictures(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    image = models.FileField(upload_to="project_images")
    title = models.CharField(max_length=20, null=True, blank=True)


class GalleryImages(models.Model):
    title = models.CharField(max_length=50)
    image = models.FileField(upload_to="galleryimages")
    CATEGORY_CHOICES = (
        ("Completed Projects Photos", "Completed Projects Photos"),
        ("Approvals & Certifications", "Approvals & Certifications"),
        ("Facility Photos", "Facility Photos"),
        ("Team Photos", "Team Photos"),
        ("Other", "Other")
    )
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    date = models.DateField(auto_now_add=True)

class TestimonialVideos(models.Model):
    client = models.CharField(max_length=50)
    video = models.FileField(upload_to="testimonial_videos")
    CATEGORY_CHOICES = (
        ("Completed Projects Photos", "Completed Projects Photos"),
        ("Approvals & Certifications", "Approvals & Certifications"),
        ("Facility Photos", "Facility Photos"),
        ("Team Photos", "Team Photos"),
        ("Other", "Other")
    )
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default="Other")
    date = models.DateField(auto_now_add=True)


class Blog(models.Model):
    blogtitle = models.CharField(max_length=100)
    image = models.FileField(upload_to='BlogImage')
    description = models.TextField()
    body = RichTextField(null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)

class Enquirys(models.Model):
    name = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)



# new for website design 


class MediaLibrary(models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.TextField()
     
    file_path = models.FileField(
        
        upload_to='uploads/',     # base path (can be empty if Laravel already used 'uploads/')
        
            # critical! keep mapping to same DB column
    )

    thumb_file_path = models.CharField(max_length=250)
    slider_file_path = models.CharField(max_length=250, blank=True, null=True)
    file_type = models.CharField(max_length=100)
    file_size = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=50, blank=True, null=True)
    media_type = models.CharField(max_length=120)
    title = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    alt_text = models.CharField(max_length=250, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="media_created")
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="media_updated")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)


    youtube_url = models.CharField(max_length=500, blank=True, null=True)

    @property
    def youtube_id(self):
        if self.youtube_url:
            import re
            match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', self.youtube_url)
            if match:
                return match.group(1)
        return None

    def __str__(self):
        return f"{str(self.file_name)} - file {self.file_type}"

class Menus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    menu_position = models.CharField(max_length=20, choices=(('header','header'),('footer',"footer")))
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="menu_created")
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="menu_updated")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)




class Services(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = CKEditor5Field(blank=True, null=True)
    image = models.FileField(upload_to="services/", blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    icon = models.CharField(max_length=100, default='bi bi-flower1', blank=True, null=True, help_text="Bootstrap Icon Class")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class MenuItems(models.Model):
    id = models.AutoField(primary_key=True)
    menus = models.ForeignKey(Menus, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=250)
    url = models.CharField(max_length=250, blank=True, null=True)
    pages = models.ForeignKey('Pages', on_delete=models.CASCADE, null=True, blank=True, related_name='menu_items')
    project = models.ForeignKey('Projects', on_delete=models.CASCADE, null=True, blank=True, related_name='menu_items')
    service = models.ForeignKey(Services, on_delete=models.CASCADE, null=True, blank=True, related_name='menu_items')
    menu_type = models.CharField(max_length=50, blank=True, null=True)
    menu_order = models.IntegerField()
    parent_id = models.ForeignKey("MenuItems", on_delete=models.CASCADE,null=True, blank=True, related_name="sub_menu")
    target_blank = models.BooleanField(default=False)
    original_title = models.CharField(max_length=250, blank=True, null=True)
    menu_nextable_id = models.CharField(max_length=250, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="menu_item_created")
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="menu_item_updated")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

        
class Pages(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    description = CKEditor5Field(blank=True, null=True)
    browser_title = models.CharField(max_length=250, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)
    media = models.ForeignKey(MediaLibrary, on_delete=models.SET_NULL, null=True, blank=True, related_name='pages_media')
    video = models.ForeignKey(MediaLibrary, on_delete=models.SET_NULL, null=True, blank=True, related_name='pages_video')
    
    # New fields for flexible page building
    PAGE_TYPE_CHOICES = (
        ('standard', 'Standard Page'),
        ('gallery', 'Gallery Page'),
        ('project', 'Project Page'),
    )
    page_type = models.CharField(max_length=50, choices=PAGE_TYPE_CHOICES, default='standard')
    custom_css = models.TextField(blank=True, null=True, help_text="Custom CSS for this page")
    extra_data = models.JSONField(blank=True, null=True, default=dict) # For storing icons, specific styles, etc.
    
    # For Gallery Pages
    gallery_images = models.ManyToManyField(MediaLibrary, related_name='page_gallery_images', blank=True)
    gallery_videos = models.ManyToManyField(MediaLibrary, related_name='page_gallery_videos', blank=True)

    status = models.IntegerField(blank=True, null=True)
    apply_button_top = models.BooleanField(default=False)
    apply_button_bottom = models.BooleanField(default=False)
    parent_id = models.ForeignKey("Pages", on_delete=models.SET_NULL, null=True, blank=True, related_name='parent_page')
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="page_created")
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="page_updated")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    
    def __str__(self):
        return self.title

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    visit_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('ip_address', 'visit_date')

    def __str__(self):
        return f"{self.ip_address} - {self.visit_date}"

class ProjectAmenity(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.project.project_title} - {self.name}: {self.value}"
