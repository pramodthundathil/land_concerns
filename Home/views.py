from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from .forms import *
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from PIL import Image
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


def Index(request):
    video = VideoSlide.objects.all().order_by('-id')[:2]
    pictures = PictureSlids.objects.all()[:4]
    projects = Projects.objects.all().order_by('order', '-created_at', '-id')[:4]
    services = Services.objects.all().order_by('order', '-created_at', '-id')[:6]
    blogs = Blog.objects.all().order_by('-id')[:2]

    if request.method == 'POST' and 'fname' in request.POST:
        # Handling the Career Portal form from the home/careers page
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        pnum = request.POST.get('pnum')
        email = request.POST.get('email')
        position = request.POST.get('position')
        message = request.POST.get('message')
        resume = request.FILES.get('resume')

        application = JobApplication(
            first_name=fname,
            last_name=lname,
            phone_number=pnum,
            email=email,
            position=position,
            message=message,
            resume=resume
        )
        application.save()
        messages.success(request, "Your application has been submitted successfully!")
        return redirect('Careers')

    context = {
       "video":video,
       "pictures":pictures,
       "projects":projects,
       "services":services,
       "blogs":blogs
    }
    return render(request,"index.html",context)

def page_detail(request, slug):
    """
    Dynamic page view for handling page URLs
    """
    page = get_object_or_404(Pages, code=slug, deleted_at__isnull=True, status=True)
    
    context = {
        "page": page
    }

    # If this is the gallery page, fetch the categorized images
    if slug == 'gallery' or page.page_type == 'gallery':
        from .models import GalleryImages
        context.update({
            "completed_projects": GalleryImages.objects.filter(category="Completed Projects Photos").order_by("-id"),
            "approvals": GalleryImages.objects.filter(category="Approvals & Certifications").order_by("-id"),
            "facility": GalleryImages.objects.filter(category="Facility Photos").order_by("-id"),
            "team": GalleryImages.objects.filter(category="Team Photos").order_by("-id"),
            "other": GalleryImages.objects.filter(category="Other").order_by("-id")
        })

    return render(request, "page_detail.html", context)

def AboutUs(request):
    return render(request,'aboutus.html')

def Testimonial(request):
    testimonial = TestimonialVideos.objects.all().order_by("-id")
    return render(request,"testimonial.html",{"testimonial":testimonial})

def Service_Architecture(request):
    return render(request,"archituture_service.html")

def Service_InteriorDesign(request):
    return render(request,"interior_design_service.html") 

def Service_Civil_Construction(request):
    return render(request,"civil_contstruction_service.html") 

def Service_Renovation(request):
    return render(request,"renovation_service.html") 

def Realestate_Renovation(request):
    return render(request,"realestate_service.html") 

def Blogs(request):
    blogs = Blog.objects.all().order_by("-id")

    context = {
       "blogs":blogs 
    }
    return render(request,"blog.html",context) 

def BlogSingle(request,pk):
    blog = Blog.objects.get(id = pk)
    return render(request,"blogsingle.html",{"blog":blog})

def Contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        enquiry = Enquirys(
            name= name,
            phone = phone,
            subject = subject,
            message = message
        )
        enquiry.save()

        # Send email to admin
        email_subject = f"New Enquiry: {subject}"
        email_message = f"Hello Admin,\n\nYou have received a new enquiry via the website.\n\n" \
                        f"Name: {name}\n" \
                        f"Phone: {phone}\n" \
                        f"Subject: {subject}\n" \
                        f"Message:\n{message}\n\n" \
                        f"Best regards,\nLand Concerns Website"
        try:
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                ['brgpillai1965@gmail.com'],
                fail_silently=True
            )
        except Exception:
            pass

        messages.info(request,"Enquiry Sent to Land Concerns... ")
        return redirect("Contact")
    return render(request,"contact.html")

def Gallery(request):
    completed_projects = GalleryImages.objects.filter(category="Completed Projects Photos").order_by("-id")
    approvals = GalleryImages.objects.filter(category="Approvals & Certifications").order_by("-id")
    facility = GalleryImages.objects.filter(category="Facility Photos").order_by("-id")
    team = GalleryImages.objects.filter(category="Team Photos").order_by("-id")
    other = GalleryImages.objects.filter(category="Other").order_by("-id")

    context ={
       "completed_projects": completed_projects,
       "approvals": approvals,
       "facility": facility,
       "team": team,
       "other": other
    }
    return render(request,"gallery.html",context)


def Gallery_interior(request):
    return redirect("Gallery")

def Gallery_ongoing(request):
    return redirect("Gallery")

def get_related_projects(project):
    from django.db.models import Q
    
    # 1. Tier 1: Same purpose, same category, same location (district), same price range
    related = Projects.objects.exclude(id=project.id).filter(purpose=project.purpose, project_category=project.project_category)
    
    # Location filtering
    parts = [p.strip() for p in project.project_subname.split(',')]
    loc_query = Q()
    for part in parts:
        if len(part) > 2:
            loc_query |= Q(project_subname__icontains=part)
            
    tier1_qs = related
    if loc_query:
        tier1_qs = tier1_qs.filter(loc_query)
        
    if project.price and project.price > 0:
        min_price = float(project.price) * 0.6
        max_price = float(project.price) * 1.4
        tier1_qs = tier1_qs.filter(price__gte=min_price, price__lte=max_price)
    else:
        tier1_qs = tier1_qs.filter(Q(price__isnull=True) | Q(price=0))
        
    results = list(tier1_qs[:3])
    
    # 2. Tier 2: Same purpose, same category, same location (any price)
    if len(results) < 3:
        tier2_qs = related
        if loc_query:
            tier2_qs = tier2_qs.filter(loc_query)
        for r in results:
            tier2_qs = tier2_qs.exclude(id=r.id)
        results += list(tier2_qs[:3 - len(results)])
        
    # 3. Tier 3: Same purpose, same category (any location, any price)
    if len(results) < 3:
        tier3_qs = related
        for r in results:
            tier3_qs = tier3_qs.exclude(id=r.id)
        results += list(tier3_qs[:3 - len(results)])
        
    # 4. Tier 4: Same purpose (any category, any location, any price)
    if len(results) < 3:
        tier4_qs = Projects.objects.exclude(id=project.id).filter(purpose=project.purpose)
        for r in results:
            tier4_qs = tier4_qs.exclude(id=r.id)
        results += list(tier4_qs[:3 - len(results)])
        
    return results


def project_detail(request, slug):
    project = get_object_or_404(Projects, slug=slug)
    related_projects = get_related_projects(project)
    context = {
        "project": project,
        "related_projects": related_projects
    }
    return render(request, "project_detail.html", context)

def service_detail(request, slug):
    service = get_object_or_404(Services, slug=slug)
    context = {
        "service": service
    }
    return render(request, "service_detail.html", context)


def Projects_(request):
    projects = Projects.objects.all().order_by('order', '-created_at', '-id')
    
    q = request.GET.get('q')
    category = request.GET.get('category')
    status = request.GET.get('status')
    purpose = request.GET.get('purpose')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if q:
        projects = projects.filter(
            Q(project_title__icontains=q) |
            Q(project_subname__icontains=q) |
            Q(project_description__icontains=q)
        )
    
    if category:
        projects = projects.filter(project_category=category)
        
    if status:
        projects = projects.filter(project_status=status)
        
    if purpose:
        projects = projects.filter(purpose=purpose)
        
    if min_price:
        try:
            projects = projects.filter(price__gte=float(min_price))
        except ValueError:
            pass
            
    if max_price:
        try:
            projects = projects.filter(price__lte=float(max_price))
        except ValueError:
            pass
            
    # Pagination: 20 properties per page
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        
    context = {
        'projects': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages()
    }
    return render(request, "projects.html", context)


def ServicesPage(request):
    services = Services.objects.all().order_by('order', '-created_at', '-id')
    context = {
        'services': services
    }
    return render(request, "services.html", context)


def Projects_Apartments(request):
    title = "Apartments"
    projects_list = Projects.objects.filter(project_category="Apartments").order_by("order", "-id")
    paginator = Paginator(projects_list, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        "title": title,
        "projects": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages()
    }
    return render(request, "projects.html", context)

def Projects_House(request):
    title = "House"
    projects_list = Projects.objects.filter(project_category="House").order_by("order", "-id")
    paginator = Paginator(projects_list, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        "title": title,
        "projects": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages()
    }
    return render(request, "projects.html", context)

def Projects_Commercial(request):
    title = "Commercial"
    projects_list = Projects.objects.filter(project_category="Commercial").order_by("order", "-id")
    paginator = Paginator(projects_list, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        "title": title,
        "projects": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages()
    }
    return render(request, "projects.html", context)

def Projects_Office(request):
    title = "Office"
    projects_list = Projects.objects.filter(project_category="Office Spaces").order_by("order", "-id")
    paginator = Paginator(projects_list, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        "title": title,
        "projects": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages()
    }
    return render(request, "projects.html", context)

def Projects_Renovation(request):
    title = "Renovation"
    projects_list = Projects.objects.filter(project_category="Renovation").order_by("order", "-id")
    paginator = Paginator(projects_list, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        "title": title,
        "projects": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages()
    }
    return render(request, "projects.html", context)


def ProjectSingle(request,pk):
    project = Projects.objects.get(id = pk)
    pictures = ProjectPictures.objects.filter(project = project)
    related_projects = get_related_projects(project)

    context = {
        "project":project,
        "pictures":pictures,
        "related_projects": related_projects
    }
    return render(request,"projectsingle.html",context)

def Careers(request):
    careers = Job.objects.all()

    context = {
        "careers":careers
    }
    return render(request,"careers.html",context)

def Jobapplication(request,pk):
    item = Job.objects.get(id = pk)
    if request.method == 'POST':
        # Collecting form data
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        pnum = request.POST.get('pnum')
        email = request.POST.get('email')
        education = request.POST.get('edu')
        experience = request.POST.get('experiance')
        address = request.POST.get('address')
        
        # Handling file uploads
        resume = request.FILES.get('resume')
        portfolio = request.FILES.get('folio')

        # Saving data to the model
        application = JobApplication(
            job = item,
            first_name=fname,
            last_name=lname,
            phone_number=pnum,
            email=email,
            education=education,
            experience=experience,
            address=address,
            resume=resume,
            portfolio=portfolio,
            position=item.title,
            message=f"Applied via {item.title} job post."
        )
        application.save()

        messages.success(request, "Application submitted successfully!")
        return redirect('Careers')
    context = {
        "item":item
    }
    return render(request,'jobapplication.html',context)






# AdminPannel Functions start __________________++++++++++++++++++++++++++++++++


def SignIn(request):
    if request.method == "POST":
        uname = request.POST['uname']
        pswd = request.POST['pswd']
    
        user = authenticate(request,username = uname, password = pswd)
        if user is not None:
            user = login(request,user)
            return redirect('Adminstration')
        else:
            messages.error(request,"username or password in correct")
            return redirect("SignIn")
        
    else:
        return render(request,"dashboard/login.html")
    
def SignOut(request):
    logout(request)
    return redirect("Index")

@login_required
def Adminstration(request):
    projects_count = Projects.objects.count()
    services_count = Services.objects.count()
    enquiries_count = Enquirys.objects.count()
    job_applications_count = JobApplication.objects.count()
    blogs_count = Blog.objects.count()
    gallery_count = GalleryImages.objects.count()
    
    # Visitor Analytics
    from datetime import timedelta
    today = timezone.now().date()
    today_visitors = Visitor.objects.filter(visit_date=today).count()
    
    # Last 7 days chart data
    dates = []
    counts = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = Visitor.objects.filter(visit_date=date).count()
        dates.append(date.strftime("%d %b"))
        counts.append(count)

    context = {
        "projects_count": projects_count,
        "services_count": services_count,
        "enquiries_count": enquiries_count,
        "job_applications_count": job_applications_count,
        "blogs_count": blogs_count,
        "gallery_count": gallery_count,
        "today_visitors": today_visitors,
        "visitor_dates": json.dumps(dates),
        "visitor_counts": json.dumps(counts),
    }
    return render(request,"dashboard/index.html", context)


# --------------------------------------------------------------------------------------
# Home Page edits 
# --------------------------------------------------------------------------------------

from .forms import *
def HomePageEdits(request):
    videoslids = VideoSlide.objects.all()
    pictureslids = PictureSlids.objects.all()
    pictureform = PictureSlidsForm()
    print(videoslids)

    context = {
        "videoslids":videoslids,
        "pictureslids":pictureslids,
        "pictureform":pictureform
    }
    return render(request,"dashboard/homepageedits.html",context)


def video_slide_create(request):
    if request.method == 'POST':
        video = request.FILES.get('video')
        caption = request.POST.get('caption')
        sub_headding = request.POST.get('sub_headding')
        
        # Creating and saving the VideoSlide instance
        video_slide = VideoSlide(
            video=video,
            caption=caption,
            sub_headding=sub_headding
        )
        video_slide.save()

        # Adding success message
        messages.success(request, "Video Slide created successfully!")
        return redirect('HomePageEdits')  # Replace with your redirect URL

    return redirect('HomePageEdits') 




def picture_slide_create(request):
    if request.method == 'POST':
        pictureform = PictureSlidsForm(request.POST, request.FILES)
        if pictureform.is_valid():
            pictureform.save()
            messages.success(request, "Picture Slide created successfully!")
            return redirect('HomePageEdits')
        else:
            messages.error(request, "Failed to create Picture Slide.")
            return redirect('HomePageEdits')

    return redirect('HomePageEdits')


@login_required
def edit_picture_carousal(request,pk):
    pic = PictureSlids.objects.get(id = pk)
    if request.method == 'POST':
        pictureform = PictureSlidsForm(request.POST, request.FILES, instance=pic)
        if pictureform.is_valid():
            pictureform.save()
            messages.success(request, "Picture Slide updated successfully!")
            return redirect('HomePageEdits')
        else:
            messages.error(request, "Failed to update Picture Slide.")
            return redirect('HomePageEdits')
    context = {
        "pic":pic,
        "form":PictureSlidsForm(instance=pic)
    }
    return render(request,"dashboard/edit_picture_carousal.html",context)

def DeleteVideoCarousal(request, pk):
    video = VideoSlide.objects.get(id = pk)
    if video.video:
        video.video.delete()
    video.delete()
    messages.success(request, "Video Slide Delete successfully!")
    return redirect('HomePageEdits')

def DeletepictureCarousal(request, pk):
    Pic = PictureSlids.objects.get(id = pk)
    if Pic.pictures:
        Pic.pictures.delete()
    Pic.delete()
    messages.success(request, "Video Slide Delete successfully!")
    return redirect('HomePageEdits')

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------


def BlogeEdits(request):
    blogs = Blog.objects.all()
    form = BlogForm()
    if request.method == "POST":
        # title = request.POST.get("title")
        # image = request.FILES.get("image")
        # description = request.POST.get("description")
        form = BlogForm(request.POST,request.FILES)
        if form.is_valid():

        # blog = Blog(
        #     blogtitle = title,
        #     image = image,
        #     description = description
        # )
            form.save()
            messages.success(request, "Blog created successfully!")
            return redirect("BlogeEdits")
        else:
            messages.error(request, "Something Wrong!!!!")
            return redirect("BlogeEdits")
    context = {
        "blogs":blogs,
        "form":form
    }
    return render(request,"dashboard/blog.html",context)

def BlogDelete(request,pk):
    blog = Blog.objects.get(id = pk)
    if blog.image:
        blog.image.delete()
    blog.delete()
    messages.info(request, "Blog Deleted successfully!")
    return redirect("BlogeEdits")


def EditBlog(request,pk):
    test_model_instance = get_object_or_404(Blog, id=pk)
    form = BlogForm(instance=test_model_instance)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=test_model_instance)
        if form.is_valid():
            form.save()
            return redirect("EditBlog",pk = pk)
    
     
    return render(request,"dashboard/blogedit.html",{ "form": form,
        "test_model": test_model_instance})


# --------------------------------------------------------------------------------------
# Gallery edits 
# --------------------------------------------------------------------------------------

def GalleryEdits(request):
    pictures = GalleryImages.objects.all()
    if request.method == "POST":
        image = request.FILES.get('image')
        title = request.POST.get('title')
        category = request.POST.get("gallery_category")

        images = GalleryImages(
            image = image,
            title = title,
            category = category
        )
        images.save()
        messages.info(request,'Gallery Image Saved ')
        return redirect('GalleryEdits')
    context = {
        "pictures":pictures
    }
    return render(request,"dashboard/gallery.html",context)

def DeleteGalleryImage(request,pk):
    image = GalleryImages.objects.get(id = pk)
    if image.image:
        image.image.delete()
    image.delete()
    messages.info(request,'Image deleted......')
    return redirect("GalleryEdits")

# --------------------------------------------------------------------------------------
# Job edits 
# --------------------------------------------------------------------------------------

def JobsEdits(request):
    jobs = Job.objects.all()
    applications = JobApplication.objects.all()
    context = {
       "jobs":jobs ,
       "applications":applications
    }
    return render(request,"dashboard/jobs.html",context)


def job_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        experience = request.POST.get('experience')
        education = request.POST.get('education')
        description = request.POST.get('description')
        salary = request.POST.get('salary')
        location = request.POST.get('location')
    
        
        # Create and save the Job instance
        job = Job(
            title=title,
            experience=experience,
            education=education,
            description=description,
            salary=salary,
            location=location,
           
        )
        job.save()

        # Add success message
        messages.success(request, "Job posted successfully!")
        return redirect('JobsEdits')  # Replace with your redirect URL

    return redirect('JobsEdits')

def JobDelete(request,pk):
    Job.objects.get(id = pk).delete()
    messages.info(request, "Job Deleted successfully!")
    return redirect("JobsEdits")

def JobSingleView(request,pk):
    job = get_object_or_404(Job, id=pk)
    
    if request.method == "POST":
        # Get the form data
        title = request.POST.get('title')
        education = request.POST.get('education')
        experience = request.POST.get('experiance')  # Ensure consistent spelling
        description = request.POST.get('descrition')  # Consistent name with form typo
        salary = request.POST.get('salary')
        location = request.POST.get('location')
        
        # Update the job instance with new values
        job.title = title
        job.education = education
        job.experience = experience
        job.description = description
        job.salary = salary
        job.location = location
        
        # Save the updated job
        job.save()

        # Add success message
        messages.success(request, "Job updated successfully!")
        
        # Redirect to the same page or any other page
        return redirect('JobSingleView', pk=pk) 
    context = {"job":job}
    return render(request,"dashboard/jobsingleview.html",context)



def JobApplicationSingleView(request,pk):
    jobapplication = JobApplication.objects.get(id = pk)

    context = {
        "jobapplication":jobapplication
    }
    return render(request,"dashboard/applicationsingleview.html",context)


def delete_application(request,pk):
    Jobapplications = JobApplication.objects.get(id = pk)
    if Jobapplications.resume:
        Jobapplications.resume.delete()
    if Jobapplications.portfolio:
        Jobapplications.portfolio.delete()
    Jobapplications.delete()
    messages.info(request,"Job Application deleted success.....")
    return redirect("JobsEdits")

# --------------------------------------------------------------------------------------
# Projects 
# --------------------------------------------------------------------------------------

def ProjectsEdits(request):
    projects_list = Projects.objects.all().order_by('order', '-created_at', '-id')

    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')
    purpose = request.GET.get('purpose', '')

    if q:
        projects_list = projects_list.filter(
            Q(project_title__icontains=q) |
            Q(project_subname__icontains=q) |
            Q(project_description__icontains=q)
        )

    if category:
        projects_list = projects_list.filter(project_category=category)

    if status:
        projects_list = projects_list.filter(project_status=status)

    if purpose:
        projects_list = projects_list.filter(purpose=purpose)

    paginator = Paginator(projects_list, 10)  # 10 properties per page
    page_number = request.GET.get('page')
    try:
        projects = paginator.page(page_number)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    # Fetch choices for filter dropdowns
    categories = Projects._meta.get_field('project_category').choices
    statuses = Projects._meta.get_field('project_status').choices
    purposes = Projects._meta.get_field('purpose').choices

    context = {
        "projects": projects,
        "q": q,
        "category": category,
        "status": status,
        "purpose": purpose,
        "categories": categories,
        "statuses": statuses,
        "purposes": purposes,
    }
    return render(request, "dashboard/projects.html", context)



def create_project(request):
    if request.method == 'POST':
        project_title = request.POST.get('project_title')
        project_subname = request.POST.get('project_subname')
        project_description = request.POST.get('project_description')
        land_area = request.POST.get('land_area')
        bulding_area = request.POST.get('bulding_area')
        location = request.POST.get('location')
        project_category = request.POST.get('project_category')
        project_status = request.POST.get('project_status')
        is_featured_product = bool(request.POST.get('is_featured_product'))
        client = request.POST.get('client')
        order = request.POST.get('order', 0)

        primary_image = request.FILES.get('primary_image')
        plan_image_1 = request.FILES.get('plan_image_1')
        plan_image_2 = request.FILES.get('plan_image_2')

        # Save project to the database
        new_project = Projects.objects.create(
            project_title = project_title,
            project_subname=project_subname,
            project_description=project_description,
            project_category=project_category,
            project_status=project_status,
            is_featured_product=is_featured_product,
            primary_image=primary_image,
            plan_image_1=plan_image_1,
            plan_image_2=plan_image_2,
            order=order,
        )
        new_project.save()
        messages.info(request,"Product added success.....")
        # Redirect to a success page or project list after saving
        return redirect('ProjectsEdits')  # Update the URL accordingly

    return redirect( 'ProjectsEdits')

def AddPicturesToProject(request, pk):
    project = get_object_or_404(Projects, id=pk)
    if request.method == "POST":
        image = request.FILES.get('image')
        caption = request.POST.get('caption')
        
        # Create MediaLibrary instance
        if image:
            media = MediaLibrary(
                file_path=image,
                file_name=image.name,
                title=caption,
                file_type=image.content_type,
                file_size=str(image.size),
                media_type='image',
                created_by=request.user,
                updated_by=request.user
            )
            media.save()
            project.gallery_images.add(media)
            messages.info(request, "Picture added to Project Gallery")
        else:
            messages.error(request, "No image selected")
            
        return redirect("ProjectSingleAdmin", pk=pk)
    return redirect("ProjectSingleAdmin", pk=pk)


def ProjectSingleAdmin(request,pk):
    # project  = Projects.objects.get(id = pk)
    project = get_object_or_404(Projects, id=pk)
    pictures = ProjectPictures.objects.filter(project = project)

    if request.method == 'POST':
        project.project_title = request.POST.get('project_title')
        project.project_subname = request.POST.get('project_subname')
        project.project_description = request.POST.get('project_description')
        project.project_category = request.POST.get('project_category')
        project.project_status = request.POST.get('project_status')
        project.is_featured_product = bool(request.POST.get('is_featured_product'))
        project.order = request.POST.get('order', 0)

        if 'primary_image' in request.FILES:
            project.primary_image = request.FILES['primary_image']
        if 'plan_image_1' in request.FILES:
            project.plan_image_1 = request.FILES['plan_image_1']
        if 'plan_image_2' in request.FILES:
            project.plan_image_2 = request.FILES['plan_image_2']

        project.save()

        messages.success(request, 'Project updated successfully!')
        return redirect('ProjectSingleAdmin', pk=pk)

    context = {
        "project":project,
        "pictures":pictures
    }
    return render(request,'dashboard/projectsingle.html',context)


def DeleteProject(request,pk):
    pro = Projects.objects.get(id = pk)
    if pro.primary_image:
        pro.primary_image.delete()
    if pro.plan_image_1:
        pro.plan_image_1.delete()
    if pro.plan_image_2:
        pro.plan_image_2.delete()
    pro.delete()
    messages.info(request,"Product Deleted success.....")
        # Redirect to a success page or project list after saving
    return redirect('ProjectsEdits')

def PhotodeleteFromProject(request, project_id, media_id):
    project = get_object_or_404(Projects, id=project_id)
    media = get_object_or_404(MediaLibrary, id=media_id)
    
    project.gallery_images.remove(media)
    # Optionally delete the media file if it's not used elsewhere? 
    # For fail safety, we just remove from relation. safely.
    
    messages.info(request, "Photo removed from project gallery")
    return redirect("ProjectSingleAdmin", pk=project_id)



# --------------------------------------------------------------------------------------
# Testimonial edits 
# --------------------------------------------------------------------------------------
def TestimonialAdmin(request):
    testimonial = TestimonialVideos.objects.all()
    if request.method =="POST":
        video = request.FILES.get("video")
        client = request.POST.get("client")
        testi = TestimonialVideos(
            video = video,
            client = client
        )
        testi.save()
        messages.info(request,"Testimonial addedeted success.....")
        return redirect("TestimonialAdmin")

    context = {
        "testimonial":testimonial
    }
    return render(request,"dashboard/testimonial.html",context)

def DeleteTestimonial(request,pk):
    testimonial = TestimonialVideos.objects.get(id = pk)
    if testimonial.video:
        testimonial.video.delete()
    testimonial.delete()
    messages.info(request,"Testimonial Deleted success.....")
    return redirect("TestimonialAdmin")
    

def Enquiry(request):
    enquiry = Enquirys.objects.all()

    return render(request,"dashboard/enquiry.html",{"enquiry":enquiry})

def DeleteEnquiry(request,pk):
    Enquirys.objects.get(id = pk).delete()
    messages.info(request,"Enquiry Deleted success.....")
    return redirect("Enquiry")








# admin new functionality 

def menu_list(request):
    menus = Menus.objects.filter(deleted_at__isnull=True).order_by('-created_at')
    context = {
        'menus': menus,
        'page_title': 'Menu Management'
    }
    return render(request, 'dashboard/admin/menu_list.html', context)

def menu_create(request):
    if request.method == 'POST':
        form = MenusForm(request.POST)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.created_by = request.user
            menu.updated_by = request.user
            menu.save()
            messages.success(request, 'Menu created successfully!')
            return redirect('menu_builder', pk=menu.pk)
    else:
        form = MenusForm()
    
    context = {
        'form': form,
        'page_title': 'Create Menu'
    }
    return render(request, 'dashboard/admin/menu_create.html', context)

def menu_builder(request, pk):
    menu = get_object_or_404(Menus, pk=pk)
    
    # Fetch all items
    items = menu.items.all().order_by('menu_order')
    
    # Build tree
    def build_tree(items):
        item_dict = {item.id: item for item in items}
        roots = []
        for item in items:
            item.children = [] # Initialize children list
        
        for item in items:
            if item.parent_id:
                parent = item_dict.get(item.parent_id.id)
                if parent:
                    parent.children.append(item)
                else:
                    # Parent might be deleted or not found, treat as root for safety
                    roots.append(item)
            else:
                roots.append(item)
        return roots

    menu_tree = build_tree(items)
    
    # Forms
    if request.method == 'POST':
        form = MenusForm(request.POST, instance=menu)
        if form.is_valid():
            menu = form.save()
            messages.success(request, 'Menu updated successfully!')
            return redirect('menu_builder', pk=pk)
    else:
        form = MenusForm(instance=menu)

    # Empty item form for the "Add Item" modal
    item_form = MenuItemsForm()
    
    # Also need pages for the dropdown? MenuItemsForm handles it via ModelChoiceField.

    context = {
        'menu': menu,
        'form': form,
        'menu_tree': menu_tree, # Pass the tree instead of flat list
        'item_form': item_form,
        'page_title': f'Builder: {menu.name}'
    }
    return render(request, 'dashboard/admin/menu_builder.html', context)

def menu_delete(request, pk):
    menu = get_object_or_404(Menus, pk=pk)
    # Soft delete
    import datetime
    menu.deleted_at = datetime.datetime.now()
    menu.save()
    messages.success(request, 'Menu deleted successfully!')
    return redirect('menu_list')

# Menu Item Views

def menu_item_create(request):
    if request.method == 'POST':
        form = MenuItemsForm(request.POST)
        menu_id = request.POST.get('menu_id')
        menu_type = request.POST.get('menu_type')
        
        if form.is_valid():
            item = form.save(commit=False)
            item.menus_id = menu_id
            item.menu_type = menu_type
            
            # Checkbox handling
            item.target_blank = True if request.POST.get('target_blank') else False
            
            # Logic to populate URL based on type
            # Logic to populate URL based on type
            if menu_type == 'page':
                # Derive URL from Page Code
                if item.pages:
                    code = item.pages.code
                    # Ensure it starts with /
                    item.url = f"/{code.strip('/')}"
                item.project = None
                item.service = None
            elif menu_type == 'project':
                if item.project:
                    item.url = f"project/{item.project.slug}"
                item.pages = None
                item.service = None
            elif menu_type == 'service':
                if item.service:
                    item.url = f"service/{item.service.slug}"
                item.pages = None
                item.project = None
            elif menu_type == 'custom':
                 # Ensure valid URL format if needed, or just trust input
                if item.url and not (item.url.startswith('http://') or item.url.startswith('https://')):
                     item.url = 'http://' + item.url
                item.pages = None # Clear Page
                item.project = None
                item.service = None
            elif menu_type == 'internal':
                # Ensure starts with /
                if item.url and not item.url.startswith('/'):
                    item.url = '/' + item.url
                item.pages = None # Clear Page
                item.project = None
                item.service = None
            elif menu_type == 'blog_link':
                item.url = 'Blogs'
                item.pages = None
                item.project = None
                item.service = None
            elif menu_type == 'job_link':
                item.url = 'Careers'
                item.pages = None
                item.project = None
                item.service = None
            elif menu_type == 'testimonial_link':
                item.url = 'Testimonial'
                item.pages = None
                item.project = None
                item.service = None
            elif menu_type == 'no_link':
                item.url = '#'
                item.pages = None
                item.project = None
                item.service = None
            
            # Default order to end
            last_item = MenuItems.objects.filter(menus_id=menu_id).order_by('-menu_order').first()
            item.menu_order = (last_item.menu_order + 1) if last_item else 0
            
            item.created_by = request.user
            item.updated_by = request.user
            item.save()
            messages.success(request, 'Menu item added!')
            return redirect('menu_builder', pk=menu_id)
        else:
             messages.error(request, 'Error adding item')
             return redirect('menu_builder', pk=menu_id)

def menu_item_update(request, pk):
    item = get_object_or_404(MenuItems, pk=pk)
    if request.method == 'POST':
        form = MenuItemsForm(request.POST, instance=item)
        menu_type = request.POST.get('menu_type')
        
        if form.is_valid():
            updated_item = form.save(commit=False)
            updated_item.menu_type = menu_type
            
            # Checkbox handling: if present in post data, it's checked (True). If missing, it's unchecked (False).
            updated_item.target_blank = True if request.POST.get('target_blank') else False
            
            # Logic to populate URL based on type
            # Logic to populate URL based on type
            if menu_type == 'page':
                 if updated_item.pages:
                    code = updated_item.pages.code
                    updated_item.url = f"/{code.strip('/')}"
                 updated_item.project = None
                 updated_item.service = None
            elif menu_type == 'project':
                if updated_item.project:
                    updated_item.url = f"/project/{updated_item.project.slug}"
                updated_item.pages = None
                updated_item.service = None
            elif menu_type == 'service':
                if updated_item.service:
                    updated_item.url = f"/service/{updated_item.service.slug}"
                updated_item.pages = None
                updated_item.project = None
            elif menu_type == 'custom':
                if updated_item.url and not (updated_item.url.startswith('http://') or updated_item.url.startswith('https://')):
                     updated_item.url = 'http://' + updated_item.url
                updated_item.pages = None
                updated_item.project = None
                updated_item.service = None
            elif menu_type == 'internal':
                if updated_item.url and not updated_item.url.startswith('/'):
                    updated_item.url = '' + updated_item.url
                updated_item.pages = None
                updated_item.project = None
                updated_item.service = None
            elif menu_type == 'blog_link':
                updated_item.url = 'Blogs'
                updated_item.pages = None
                updated_item.project = None
                updated_item.service = None
            elif menu_type == 'job_link':
                updated_item.url = 'Careers'
                updated_item.pages = None
                updated_item.project = None
                updated_item.service = None
            elif menu_type == 'testimonial_link':
                updated_item.url = 'Testimonial'
                updated_item.pages = None
                updated_item.project = None
                updated_item.service = None
            elif menu_type == 'no_link':
                updated_item.url = '#'
                updated_item.pages = None
                updated_item.project = None
                updated_item.service = None
                
            updated_item.save()
            messages.success(request, 'Item updated!')
        else:
            messages.error(request, 'Error updating item')
    return redirect('menu_builder', pk=item.menus.pk)

def refresh_menu_urls(request, pk):
    menu = get_object_or_404(Menus, pk=pk)
    items = menu.items.all()
    count = 0
    
    for item in items:
        changed = False
        if item.menu_type == 'page' and item.pages:
            new_url = f"{item.pages.code.strip('/')}"
            if item.url != new_url:
                item.url = new_url
                changed = True
        elif item.menu_type == 'project' and item.project:
            new_url = f"project/{item.project.slug}"
            if item.url != new_url:
                item.url = new_url
                changed = True
        elif item.menu_type == 'service' and item.service:
            new_url = f"service/{item.service.slug}"
            if item.url != new_url:
                item.url = new_url
                changed = True
        elif item.menu_type == 'custom' and item.url:
             if not (item.url.startswith('http://') or item.url.startswith('https://')):
                 item.url = 'http://' + item.url
                 changed = True
        elif item.menu_type == 'internal' and item.url:
             if not item.url.startswith('/'):
                 item.url = '' + item.url
                 changed = True
        
        if changed:
            item.save()
            count += 1
            
    messages.success(request, f'Refreshed URLs for {count} items!')
    return redirect('menu_builder', pk=pk)

def menu_item_delete(request, pk):
    item = get_object_or_404(MenuItems, pk=pk)
    menu_pk = item.menus.pk
    item.delete() 
    messages.success(request, 'Item removed!')
    return redirect('menu_builder', pk=menu_pk)

@csrf_exempt
def update_menu_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            menu_data = data.get('menu_data') # Should be the nestable JSON
            
            # Helper function to recursively update order and parent
            def update_items(items, parent_id=None):
                for index, item_data in enumerate(items):
                    item_id = item_data.get('id')
                    item = MenuItems.objects.get(pk=item_id)
                    item.menu_order = index
                    item.parent_id_id = parent_id # Update parent
                    item.save()
                    
                    if 'children' in item_data:
                        update_items(item_data['children'], parent_id=item_id)
            
            update_items(menu_data)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid request'}, status=400)


# --------------------------------------------------------------------------------------
# Page Admin Views
# --------------------------------------------------------------------------------------


def media_library_json(request):
    """
    Returns a JSON list of media files for the media selector.
    Supports pagination and search.
    """
    page_number = request.GET.get('page', 1)
    search_query = request.GET.get('search', '')
    
    media_list = MediaLibrary.objects.all().order_by('-created_at')
    
    if search_query:
        media_list = media_list.filter(file_name__icontains=search_query)
        
    per_page = 18 # 6x3 grid
    paginator = Paginator(media_list, per_page)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, return empty list (for infinite scroll/load more)
        page_obj = []

    data = []
    has_next = False
    next_page_number = None

    if hasattr(page_obj, 'has_next'):
        has_next = page_obj.has_next()
        if has_next:
            next_page_number = page_obj.next_page_number()

    if page_obj:
        for media in page_obj:
            # Determine thumbnail URL
            thumb_url = ''
            if media.media_type == 'image' and media.file_path:
                try:
                    thumb_url = media.file_path.url
                except:
                    thumb_url = ''
            elif media.media_type == 'video':
                 if media.youtube_url:
                     # Attempt to extract video ID for thumbnail
                     try:
                        import re
                        video_id = ""
                        # Regex for standard and shortened YouTube URLs
                        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', media.youtube_url)
                        if match:
                            video_id = match.group(1)
                            thumb_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                        else:
                            thumb_url = '/static/admin/img/video-icon.png'
                     except:
                         thumb_url = '/static/admin/img/video-icon.png'
                 else:
                    thumb_url = '/static/admin/img/video-icon.png' # Placeholder for local video
            else:
                 thumb_url = '/static/admin/img/file-icon.png' # Placeholder

            data.append({
                'id': media.id,
                'name': media.file_name,
                'url': media.youtube_url if media.youtube_url else (media.file_path.url if media.file_path else ''),
                'thumb': thumb_url,
                'type': media.media_type,
                'dimensions': media.dimensions,
                'size': media.file_size
            })
            
    return JsonResponse({
        'success': True,
        'data': data,
        'has_next': has_next,
        'next_page': next_page_number
    })


@require_POST
def media_library_upload_json(request):
    """
    Handles AJAX file uploads for the media library selector.
    """
    description = request.POST.get('description', '')

    if 'youtube_url' in request.POST:
        try:
            youtube_url = request.POST.get('youtube_url')
            if not youtube_url:
                 return JsonResponse({'success': False, 'message': 'No URL provided'})
            
            media = MediaLibrary()
            media.file_name = "YouTube Video" # or extract title?
            media.youtube_url = youtube_url
            media.description = description
            media.file_type = "youtube"
            media.file_size = "0 KB"
            media.created_by = request.user
            media.updated_by = request.user
            media.created_at = timezone.now()
            media.thumb_file_path = ""
            media.media_type = 'video'
            
            # extract name from url if possible or keep generic
            import re
            match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
            if match:
                 media.file_name = f"YouTube: {match.group(1)}"

            media.save()
            
            # thumbnail for response
            thumb = '/static/admin/img/video-icon.png'
            if match:
                thumb = f"https://img.youtube.com/vi/{match.group(1)}/0.jpg"

            return JsonResponse({
                'success': True,
                'media': {
                    'id': media.id,
                    'name': media.file_name,
                    'url': media.youtube_url,
                    'thumb': thumb
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    if 'file' in request.FILES:
        try:
            uploaded_file = request.FILES['file']
            
            media = MediaLibrary()
            media.file_name = uploaded_file.name
            media.description = description
            media.file_path = uploaded_file
            media.file_type = uploaded_file.name.split('.')[-1].lower()
            media.file_size = f"{uploaded_file.size / 1024:.2f} KB"
            media.created_by = request.user
            media.updated_by = request.user
            media.created_at = timezone.now()
            # Fix: thumb_file_path is required in model but was missing here
            media.thumb_file_path = "" 
            
            # Dimension check for images
            if media.file_type in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                try:
                    img = Image.open(uploaded_file)
                    media.dimensions = f"{img.width}x{img.height}"
                    media.media_type = 'image'
                except:
                    media.media_type = 'file'
            elif media.file_type in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm']:
                 media.media_type = 'video'
            else:
                media.media_type = 'file'
                
            media.save()
            
            # Return the new media object data
            return JsonResponse({
                'success': True,
                'media': {
                    'id': media.id,
                    'name': media.file_name,
                    'url': media.file_path.url,
                    'thumb': media.file_path.url if media.media_type == 'image' else '/static/admin/img/file-icon.png'
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
            
    return JsonResponse({'success': False, 'message': 'No file or URL provided'})



def page_list(request):
    pages = Pages.objects.filter(deleted_at__isnull=True).order_by('-created_at')
    context = {
        'pages': pages,
        'page_title': 'Page Management'
    }
    return render(request, 'dashboard/admin/pages/page_list.html', context)

def page_create(request):
    if request.method == 'POST':
        form = PagesForm(request.POST, request.FILES)
        if form.is_valid():
            page = form.save(commit=False)
            page.created_by = request.user
            page.updated_by = request.user
            page.save()
            form.save_m2m() # Critical for saving M2M fields like gallery_images
            messages.success(request, 'Page created successfully!')
            return redirect('page_list')
    else:
        form = PagesForm()

    # Get all media for selection dropdowns (if using native select widgets in form)
    # The form already has ModelChoiceFields for media/video, so they will be populated.
    
    context = {
        'form': form,
        'page_title': 'Create Page',
        "action": "Edit Page"
        
    }
    return render(request, 'dashboard/admin/pages/page_form.html', context)

def page_edit(request, pk):
    page = get_object_or_404(Pages, pk=pk)
    if request.method == 'POST':
        form = PagesForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            page = form.save(commit=False)
            page.updated_by = request.user
            page.save()
            form.save_m2m() # Critical for saving M2M fields like gallery_images
            messages.success(request, 'Page updated successfully!')
            return redirect('page_list')
    else:
        form = PagesForm(instance=page)
    
    context = {
        'form': form,
        'page': page,
        'page_title': 'Edit Page',
        "action": "Save Update"
    }
    return render(request, 'dashboard/admin/pages/page_form.html', context)


# --------------------------------------------------------------------------------------
# Project Admin Views (New)
# --------------------------------------------------------------------------------------

def project_add(request):
    if request.method == 'POST':
        form = ProjectsForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m() 
            
            # Save amenities
            names = request.POST.getlist('amenity_name[]')
            values = request.POST.getlist('amenity_value[]')
            for name, val in zip(names, values):
                if name.strip() and val.strip():
                    ProjectAmenity.objects.create(project=project, name=name.strip(), value=val.strip())
                    
            messages.success(request, 'Project created successfully!')
            return redirect('ProjectsEdits') # Redirect to list
        else:
             messages.error(request, 'Error creating project. Please check the form.')
    else:
        form = ProjectsForm()

    context = {
        'form': form,
        'page_title': 'Add Project',
        'action': 'Create'
    }
    return render(request, 'dashboard/admin/projects/project_form.html', context)

def project_edit(request, pk):
    project = get_object_or_404(Projects, pk=pk)
    if request.method == 'POST':
        form = ProjectsForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m()
            
            # Handle deletions of existing gallery pictures after save_m2m
            delete_pics = request.POST.getlist('delete_pics')
            if delete_pics:
                ProjectPictures.objects.filter(id__in=delete_pics, project=project).delete()
                
            delete_gallery = request.POST.getlist('delete_gallery')
            if delete_gallery:
                project.gallery_images.remove(*delete_gallery)
            
            # Update amenities: delete existing ones and recreate
            project.amenities.all().delete()
            names = request.POST.getlist('amenity_name[]')
            values = request.POST.getlist('amenity_value[]')
            for name, val in zip(names, values):
                if name.strip() and val.strip():
                    ProjectAmenity.objects.create(project=project, name=name.strip(), value=val.strip())
                    
            messages.success(request, 'Project updated successfully!')
            return redirect('project_edit', pk=pk)
        else:
            messages.error(request, 'Error updating project.')
    else:
        form = ProjectsForm(instance=project)

    context = {
        'form': form,
        'project': project,
        'page_title': 'Edit Project',
        'action': 'Update'
    }
    return render(request, 'dashboard/admin/projects/project_form.html', context)


# --------------------------------------------------------------------------------------
# Service Admin Views
# --------------------------------------------------------------------------------------

def service_list(request):
    services = Services.objects.all().order_by('order', '-created_at')
    context = {
        'services': services,
        'page_title': 'Service Management'
    }
    return render(request, 'dashboard/admin/services/service_list.html', context)

def service_create(request):
    if request.method == 'POST':
        form = ServicesForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, 'Service created successfully!')
            return redirect('service_list')
        else:
            messages.error(request, 'Error creating service.')
    else:
        form = ServicesForm()

    context = {
        'form': form,
        'page_title': 'Add Service',
        'action': 'Create'
    }
    return render(request, 'dashboard/admin/services/service_form.html', context)

def service_update(request, pk):
    service = get_object_or_404(Services, pk=pk)
    if request.method == 'POST':
        form = ServicesForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            service = form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('service_list')
        else:
            messages.error(request, 'Error updating service.')
    else:
        form = ServicesForm(instance=service)

    context = {
        'form': form,
        'service': service,
        'page_title': 'Edit Service',
        'action': 'Update'
    }
    return render(request, 'dashboard/admin/services/service_form.html', context)

def service_delete(request, pk):
    service = get_object_or_404(Services, pk=pk)
    service.delete()
    messages.success(request, 'Service deleted successfully!')
    return redirect('service_list')


def page_delete(request, pk):
    page = get_object_or_404(Pages, pk=pk)
    import datetime
    page.deleted_at = datetime.datetime.now()
    page.save()
    messages.success(request, 'Page deleted successfully!')
    return redirect('page_list')
