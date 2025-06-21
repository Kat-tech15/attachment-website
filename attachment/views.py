from datetime import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms  import AuthenticationForm, UserCreationForm 
from django.contrib.auth import login, logout, authenticate , get_user_model 
from django.http import HttpResponseForbidden 
from .models import Attachee, Company, House, AttachmentApplication, Booking, AttachmentPost,Company,Contact, RentalListing
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.utils import timezone
from .forms import AttachmentPostForm, HouseForm, AttachmentApplicationForm
# Create your views here.



user = get_user_model()


def home(request):
    query = request.GET.get('q')
    if query:
        applications = Attachee.objects.filter(name__icontains=query)
    else:
        applications = Attachee.objects.all()

    return render(request, 'home.html',{'applications': applications})

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

    

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')

                role = user.role
                if role == 'admin':
                    return redirect('admin_dashboard')

                elif role == 'attachee':
                    return redirect('attachee_dashboard')       

                elif role == 'company':
                    return redirect('company_dashboard')

                elif role == 'tenant':
                    return redirect('tenants_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")

        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form}) 
    
      
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            if user.role == 'company':
                Company.objects.create(
                    user=user,
                    name=user.username,
                    email=user.email,
                    phone_number='',
                    location=''
                )

            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request,'registration/register.html', {'form': form})

def contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email =request.POST.get('email')
        message = request.POST.get('message')

        contact = Contact.objects.create(
            full_name=full_name,
            email=email,
            message=message,
        )

        contact.save()
        messages.success(request, 'Your message has been sent successfully!')   
        return redirect('contact')

    return render(request, 'contact.html')

# Attachee's views



def my_applications(request):
    if request.user.role != 'attachee':
        return HttpResponseForbidden("Only attachees have access to this page.")
    
    applications = AttachmentApplication.objects.filter(attachee__user=request.user)
    return render(request, 'my_applications.html', {'applications': applications})

def attachee_list(request):
    applications = Attachee.objects.all()
    return render(request, 'attachee_list.html',{'applications': applications})

@login_required
def apply_attachment(request, attachment_id):
    if request.user.role not in ['admin', 'attachee']:
        return HttpResponseForbidden("Only attachees can apply for attachments.")

     
    try:
        attachee_instance = Attachee.objects.get(user=request.user)
        print("Attachee instance found:", attachee_instance)
    except Attachee.DoesNotExist:
        print("Attachee instance not found for user:", request.user)

        # If the user does not have an Attachee profile, redirect to home with an error message
        messages.error(request, "You need an Attachee profile to apply for attachment.")
        return redirect('view_attachments') 
    
     # Get the attachment post
    attachment_post = get_object_or_404(AttachmentPost, id=attachment_id)

    # Prevent double applications
    try: 
        application = AttachmentApplication.objects.get(attachee=attachee_instance, attachment_post=attachment_post)
        already_applied = True
    except AttachmentApplication.DoesNotExist:
        already_applied = False
        application = None

    if request.method == 'POST':
        form = AttachmentApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            new_application = form.save(commit=False)
            new_application.attachee = attachee_instance
            new_application.attachment_post = attachment_post
            new_application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('view_attachments')
    else:
        form = AttachmentApplicationForm(instance=application)

    return render(request, 'apply_attachment.html', {
        'form': form,
        'attachment_post': attachment_post,
        'already_applied': already_applied
    })

@login_required
def book_rental(request, rental_id):
    if request.user.role not in ['admin','attachee']:
        return HttpResponseForbidden("Only Admins and Attachees have access to this page.")
 
    rental_post = get_object_or_404(House, id=rental_id)

    # check if attachee exists 
    try:
        attachee = request.user.attachee
    except Attachee.DoesNotExist:
        return HttpResponseForbidden("You must complete your attachee profile first.")

    booking, created = Booking.objects.get_or_create(
        attachee = attachee,
        rental_post = rental_post,
        defaults= {
            'full_name': attachee.full_name,
            'contact': attachee.phone_number,
        }
    )
    message = "House booked successfully!" if created else "You have already booked this house."

    return render(request, 'book_rental.html', {
        'rental': rental_post,
        'message': message
    })
        

def my_bookings(request):
    if request.user.role in ['admin', 'attachee', 'tenant']:
        return HttpResponseForbidden("Only Attachees and Tenants can view bookings.")

    bookings = Booking.objects.filter(attachee=request.user).select_related('house')
    return render(request, 'my_bookings.html', {'bookings': bookings})

# Tenant's Views 

@login_required
def all_rentals(request):
    if request.user.role != 'tenant':
        return HttpResponseForbidden()

    rentals = RentalListing.objects.all()

    return render(request, 'all_rentals.html',{'rentals': rentals})

@login_required
def all_attachment_posts(request):
    if request.user.role != 'company':
        return HttpResponseForbidden("Only companies have access to this page.")
    
    
    
    own_posts = AttachmentPost.objects.filter(company__user=request.user)
    other_posts = AttachmentPost.objects.exclude(company__user=request.user)
    return render(request, 'all_attachment_posts.html', {
        'own_posts': own_posts,
        'other_posts': other_posts
    })

@login_required
def post_rental(request):
    if request.user.role not in ['admin','tenant']:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            house = form.save(commit=False)
            house.tenant = request.user.username
            house.posted_by = request.user
            house.save()
            return redirect('tenants_dashboard')
    
    else:
        form = HouseForm()

    return render(request, 'post_rental.html', {'form': form})

def make_inquiry(request):
    return render(request, 'make_inquiry.html')


def view_rentals(request):
    return render(request, 'view_rentals.html',{'rentals': House.objects.all()})


def view_attachments(request):
    return render(request, 'view_attachments.html', {'attachments': AttachmentPost.objects.all()}) 

# companys' Views 
@login_required 
def post_attachment(request):
    if request.user.role not in ['admin', 'company']:
        return HttpResponseForbidden("You have no permission to post attachments.")

    
    try:
        company = request.user.company
    except Company.DoesNotExist:
        return HttpResponseForbidden("You must complete your company profile first.")


    if request.method == 'POST':
        form = AttachmentPostForm(request.POST, user=request.user)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.company = company
            attachment.save()
            return redirect('view_attachments')
        
    else:
        form = AttachmentPostForm(user=request.user)

    return render(request, 'post_attachment.html', {'form': form})

def opportunities(request):
    return render(request, 'opportunities.html')

def view_applicants(request):
    return render(request, 'view_applicants.html')

# Login views
@login_required
def dashboard_router(request):
    role = request.user.role
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'attachee':
        return redirect('attachee_dashboard')
    elif role == 'company':
        return redirect('company_dashboard')
    elif role == 'tenant':
        return redirect('tenants_dashboard')
    else:
        return redirect(request, 'erro.html', {'message': 'unknown role'})
    

@login_required
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')

@login_required
def attachee_dashboard(request):
    house = House.objects.all()
    return render(request, 'dashboards/attachee_dashboard.html', {'house': house})

@login_required
def company_dashboard(request):
    return render(request, 'dashboards/company_dashboard.html')

@login_required
def tenants_dashboard(request):
    return render(request, 'dashboards/tenants_dashboard.html')

