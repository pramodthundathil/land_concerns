from django.urls import path 
from .import views 

urlpatterns = [
   
    path("",views.Index,name="Index"),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
    
    path("SignIn",views.SignIn,name="SignIn"),
    path("SignOut",views.SignOut,name="SignOut"),
    path("about-us",views.AboutUs,name="AboutUs"),
    path("Service_Architecture",views.Service_Architecture,name="Service_Architecture"),
    path("Service_InteriorDesign",views.Service_InteriorDesign,name="Service_InteriorDesign"),
    path("Service_Civil_Construction",views.Service_Civil_Construction,name="Service_Civil_Construction"),
    path("Service_Renovation",views.Service_Renovation,name="Service_Renovation"),
    path("Realestate_Renovation",views.Realestate_Renovation,name="Realestate_Renovation"),
    path("Blogs",views.Blogs,name="Blogs"),
    path("BlogSingle/<int:pk>",views.BlogSingle,name="BlogSingle"),
    path("contact-us/",views.Contact,name="Contact"),
    path("Gallery",views.Gallery,name="Gallery"),
    path("project/<slug:slug>/", views.project_detail, name="project_detail"),
    path("service/<slug:slug>/", views.service_detail, name="service_detail"),
    path("projects/",views.Projects_,name="Projects_"),
    path("services/",views.ServicesPage,name="ServicesPage"),

    path("Careers",views.Careers,name="Careers"),
    path("Jobapplication/<int:pk>",views.Jobapplication, name="Jobapplication"),
    path("Projects_Apartments",views.Projects_Apartments, name="Projects_Apartments"),
    path("Projects_House",views.Projects_House, name="Projects_House"),
    path("Projects_Commercial",views.Projects_Commercial, name="Projects_Commercial"),
    path("Projects_Office",views.Projects_Office, name="Projects_Office"),
    path("Projects_Renovation",views.Projects_Renovation, name="Projects_Renovation"),

    path("ProjectSingle/<int:pk>",views.ProjectSingle,name="ProjectSingle"),
    path("Testimonial",views.Testimonial,name="Testimonial"),
    

    

    # admin urls
    path("SignIn/",views.SignIn,name="Signin"),
    path("Adminstration",views.Adminstration,name="Adminstration"),
    path("HomePageEdits",views.HomePageEdits,name="HomePageEdits"),
    path('BlogeEdits', views.BlogeEdits, name='BlogeEdits'),
    path('GalleryEdits', views.GalleryEdits, name='GalleryEdits'),
    path('JobsEdits', views.JobsEdits, name='JobsEdits'),
    path('ProjectsEdits', views.ProjectsEdits, name='ProjectsEdits'),
    path('video_slide_create', views.video_slide_create, name='video_slide_create'),
   
    path('picture_slide_create', views.picture_slide_create, name='picture_slide_create'),
    path('edit_picture_carousal/<int:pk>', views.edit_picture_carousal, name='edit_picture_carousal'),
    
    path('job_create', views.job_create, name='job_create'),
    path('JobApplicationSingleView/<int:pk>', views.JobApplicationSingleView, name='JobApplicationSingleView'),
    path('delete_application/<int:pk>', views.delete_application, name='delete_application'),
    path('JobDelete/<int:pk>', views.JobDelete, name='JobDelete'),
    path('JobSingleView/<int:pk>', views.JobSingleView, name='JobSingleView'),
    path('create_project', views.create_project, name='create_project'),
    path("DeleteProject/<int:pk>",views.DeleteProject,name="DeleteProject"),
    path("ProjectSingleAdmin/<int:pk>",views.ProjectSingleAdmin,name="ProjectSingleAdmin"),
    path("AddPicturesToProject/<int:pk>",views.AddPicturesToProject,name="AddPicturesToProject"),
    path("PhotodeleteFromProject/<int:project_id>/<int:media_id>",views.PhotodeleteFromProject,name="PhotodeleteFromProject"),
    
    # New Project Admin URLs
    path('site/admin/projects/add/', views.project_add, name='project_add'),
    path('site/admin/projects/edit/<int:pk>/', views.project_edit, name='project_edit'),

    # Service Admin URLs
    path('site/admin/services/', views.service_list, name='service_list'),
    path('site/admin/services/create/', views.service_create, name='service_create'),
    path('site/admin/services/edit/<int:pk>/', views.service_update, name='service_update'),
    path('site/admin/services/delete/<int:pk>/', views.service_delete, name='service_delete'),


    path("DeleteGalleryImage/<int:pk>",views.DeleteGalleryImage,name="DeleteGalleryImage"),

    path("TestimonialAdmin",views.TestimonialAdmin,name="TestimonialAdmin"),
    path("DeleteTestimonial/<int:pk>",views.DeleteTestimonial,name="DeleteTestimonial"),
    path("BlogDelete/<int:pk>",views.BlogDelete,name="BlogDelete"),
    path("Enquiry",views.Enquiry,name="Enquiry"),
    path("DeleteEnquiry/<int:pk>",views.DeleteEnquiry,name="DeleteEnquiry"),
    path("DeletepictureCarousal/<int:pk>",views.DeletepictureCarousal,name="DeletepictureCarousal"),
    path("DeleteVideoCarousal/<int:pk>",views.DeleteVideoCarousal,name="DeleteVideoCarousal"),
    path("Gallery_interior",views.Gallery_interior,name="Gallery_interior"),
    path("Gallery_ongoing",views.Gallery_ongoing,name="Gallery_ongoing"),

    path("EditBlog/<int:pk>",views.EditBlog,name="EditBlog"),
    
    
    
    # admin new functinality 
    path('site/admin/menus/', views.menu_list, name='menu_list'),
    path('site/admin/menus/create/', views.menu_create, name='menu_create'),
    path('site/admin/menus/edit/<int:pk>/', views.menu_builder, name='menu_builder'),
    path('site/admin/menus/delete/<int:pk>/', views.menu_delete, name='menu_delete'),
    
    path('site/admin/menus/items/create/', views.menu_item_create, name='menu_item_create'),
    path('site/admin/menus/items/update/<int:pk>/', views.menu_item_update, name='menu_item_update'),
    path('site/admin/menus/items/delete/<int:pk>/', views.menu_item_delete, name='menu_item_delete'),
    path('site/admin/menus/items/reorder/', views.update_menu_order, name='update_menu_order'),
    path('site/admin/menus/items/refresh/<int:pk>/', views.refresh_menu_urls, name='refresh_menu_urls'),

    # Page Admin URLs
    path('site/admin/pages/', views.page_list, name='page_list'),
    path('site/admin/pages/create/', views.page_create, name='page_create'),
    path('site/admin/pages/edit/<int:pk>/', views.page_edit, name='page_edit'),
    path('site/admin/pages/delete/<int:pk>/', views.page_delete, name='page_delete'),
    
    # Media Library JSON API
    path('site/admin/media/json/', views.media_library_json, name='media_library_json'),
    path('site/admin/media/upload/json/', views.media_library_upload_json, name='media_library_upload_json'),



   

]