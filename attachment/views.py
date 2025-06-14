from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms  import AuthenticationForm, UserCreationForm 
from django.contrib.auth import login, logout, authenticate , get_user_model 
from django.http import HttpResponseForbidden 
from .models import Attachee, Company, House, AttachmentApplication, Booking, AttachmentPost,Company,Contact
from .forms import CustomUserCreationForm
from django.contrib import messages
from .forms import AttachmentPostForm, HouseForm
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


def accomodation(request):
    return render(request, 'accomodation.html')

def my_applications(request):
    return render(request, 'my_applications.html')

def attachee_list(request):
    applications = Attachee.objects.all()
    return render(request, 'attachee_list.html',{'applications': applications})

@login_required
def apply_attachment(request, attachment_id):
    if request.user.role not in ['admin','attachee']:
        return HttpResponseForbidden("Only attachees can apply for attachments.")

    attachment_post  = get_object_or_404(AttachmentPost, id=attachment_id)
    attachee,_=get_object_or_404(Attachee, user=request.user)

    # check if the user already applied
    application, created = Attachee.objects.get_or_create(
        attachee,_ = attachee,
        attachment_post = attachment_post,
        defaults={
            'cv': 'cv_placeholder.jpg',
            'cover_letter': 'cover_letter_placeholder.jpg',
            'recommendation': 'recommendation_placeholder.jpg',
            'preferred_start': '2025-07-02',

        }
    )

    if created:
        message = "Application submitted successfully!"
    else:
        message ="You have already applied for this post."

    return render(request, 'apply_attachment.html', {
        'attachment': attachment_post,
        'message': message
    })

@login_required
def book_rental(request, rental_id):
    if request.user.role not in ['admin','attachee']:
        return HttpResponseForbidden("Only Admins and Attachees have access to this page.")

    rental_post = get_object_or_404(House, id=rental_id)

    booking, booked = Booking.objects.get_or_create(
        attachee = request.user,
        rental_post = rental_post,
        defaults= {
            'full_name': request.user.attachee.full_name,
            'contact': request.user.attachee.contact,
            'board_date': '2025-07-02',
        }
    )
    if booked:
        message = "House booked sucessfully!"
    else:
        message = "You have already booked this house."

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


def rentals(request):
    return render(request, 'rentals.html')


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

