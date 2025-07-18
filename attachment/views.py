from datetime import timezone, timedelta
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import status
from notifications.signals import notify
from django.template.loader import render_to_string
from weasyprint import HTML
from xhtml2pdf import pisa
from django.db.models import Count,Avg
from django.core.mail import EmailMessage
import tempfile
from django.db.models.signals import post_save
from django.views.decorators.http import require_POST
from django.dispatch import receiver
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms  import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate , get_user_model 
from django.http import HttpResponseForbidden, HttpResponse
from .models import CustomUser, Attachee, Company, House, AttachmentApplication, Booking, AttachmentPost,Company,Contact, Room, Notification, Tenant,Testimonials, Feedback
from .forms import CustomUserCreationForm,HouseForm,FeedbackForm
from django.contrib import messages
from django.utils import timezone
from .forms import AttachmentPostForm, HouseForm,BookingForm, AttachmentApplicationForm, HouseReviewForm, CompanyReviewForm

# Create your views here.



user = get_user_model()
is_superuser = True
is_staff =True


def home(request):
    featured_houses = House.objects.all().order_by('?')[:4]
    recent_attachments = AttachmentPost.objects.order_by('-id')[:2]
    testimonials = Testimonials.objects.all()[:5]
    query = request.GET.get('q')
    if query:
        applications = Attachee.objects.filter(name__icontains=query)
    else:
        applications = Attachee.objects.all()
    form = FeedbackForm()

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('home')
        else:
            form = FeedbackForm()

    return render(request, 'home.html',{
        'form': form,
        'applications': applications,
        'featured_houses': featured_houses,
        'recent_attachments': recent_attachments,
        'testimonials': testimonials
        })

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
                
                if user.is_superuser or user.is_staff:
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

            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
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
    if not request.user.has_priviledge(['attachee']):
        return HttpResponseForbidden("Only attachees have access to this page.")
    
    applications = AttachmentApplication.objects.filter(attachee__user=request.user)
    return render(request, 'my_applications.html', {'applications': applications})

def attachee_list(request):
    applications = Attachee.objects.all()
    return render(request, 'attachee_list.html',{'applications': applications})

@login_required
def apply_attachment(request, attachment_id):
    if not request.user.has_priviledge(['attachee']):
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

@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def approve_application(request, app_id):
    app = get_object_or_404(AttachmentApplication, id=app_id)
    app.status = 'approved'
    app.save()

    notify.send(
        sender=request.user,
        recipient=app.attacheee,
        verb='Your attachment application was approved',
        data={'url': f'/attachee/my_applications/{app.id}/'}
    )

    return redirect('admin_dashboard')


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def reject_application(request, app_id):
    app = get_object_or_404(AttachmentApplication, id=app_id)
    app.status= 'rejected'
    app.save()

    notify.send(
        sender= request.uer,
        recipient= app.attachee,
        verb='Your attachment application was rejected',
        data={'url': f'/attachee/my_applications/{app.id}/'}
    )

    return redirect('admin_dashboard')


def my_bookings(request):
    if not request.user.has_priviledge(['attachee', 'tenant']) and not request.user.is_superuser:
        return HttpResponseForbidden("Only Attachees and Tenants can view bookings.")

    if request.user.is_superuser:
        bookings = Booking.objects.all().select_related('room','house_post', 'attachee')
    elif hasattr(request.user, 'attachee'):
        bookings = Booking.objects.filter(
            attachee=request.user.attachee
        ).exclude(
            status='cancelled'
        ).select_related('room', 'house_post', 'attachee')
    else:
        return HttpResponseForbidden("You must be an attachee  to view your bookings.")
    today = timezone.now().date()
    
    return render(request, 'my_bookings.html', {
        'bookings': bookings,
        'today': today,
    })

# Tenant's Views 
def tenant_house_bookings(request):
    if not request.user.is_superuser and not request.user.has_priviledge(['tenant']):
        HttpResponseForbidden("Only tenants can access this page.")
    
    if request.user.is_superuser:
        bookings = Booking.objects.all().select_related('room', 'attachee')
    else:
        try:
            tenant_rooms = Room.objects.filter(house__tenant=request.user)
            bookings = Booking.objects.filter(room__in=tenant_rooms).select_related('room', 'room__house', 'attachee')
        except Room.DoesNotExist:
            bookings = []

    return render(request, 'tenant_house_bookings.html', {
        'bookings': bookings,
        'today': timezone.now().date()
    })

@login_required
def all_houses(request):
    if not request.user.has_priviledge(['tenant']):
        return HttpResponseForbidden()

    houses = House.objects.all().prefetch_related('tenant')
    for house in houses:
        house.available_rooms =house.rooms.filter(is_booked=False).count()
        house.booked_rooms = house.rooms.filter(is_booked=True).count()
        house.total_rooms = house.rooms.count()

    return render(request, 'all_houses.html',{'houses': houses})

@receiver(post_save, sender=House)
def create_room(sender, instance, created, **kwargs):
    if created:
        for i in range(1, instance.total_rooms + 1):
            Room.objects.create(
                house=instance,
                room_number=f"{i}",
                price= instance.rent,
                room_type=instance.description)

@login_required
def book_room(request, room_id):
    if not request.user.has_priviledge(['tenant','attachee']):
        return HttpResponseForbidden("Only tenants and attachees can book rooms.")
    
    

    room = get_object_or_404(Room, id=room_id)
    house = room.house

    if room.is_booked:
        messages.warning(request, "Sorry, this room is already booked.")
        return redirect('all_houses')

    
    attachee = None
    full_name = "Admin"
    phone_number = "N/A"

    
    if request.user.has_priviledge(['tenant']) and not (request.user.is_superuser or request.user.is_staff):
        try:
            attachee = request.user.attachee
            full_name = attachee.full_name
            contact = attachee.phone_number
        except Attachee.DoesNotExist:
            messages.error(request, "You need to be an Attachee to book a room.")
            return redirect('all_houses')

    booking = Booking.objects.create(
        attachee=attachee,
        house_post=room.house,
        room=room,
        full_name=full_name,
        phone_number=phone_number,
        move_in_date=timezone.now().date(),
    )
    room.is_booked = True
    room.save()

    messages.success(request, f"Room{room.room_number} booked successfully!")

    return redirect('house_detail', house_id=house.id)

def house_detail(request, house_id):
    house = get_object_or_404(House, id=house_id)

    rooms = Room.objects.filter(house=house)
    available_rooms = rooms.filter(is_booked=False)
    booked_rooms = rooms.filter(is_booked=True)
    return render(request, 'house_detail.html', {
        'house': house,
        'available_rooms': available_rooms,
        'booked_rooms': booked_rooms,
    })  


@login_required
def all_attachment_posts(request):
    if not request.user.has_priviledge(['company']):
        return HttpResponseForbidden("Only companies have access to this page.")
    
    query = request.GET.get('q')
    sort = request.GET.get('sort')

    attachments = AttachmentPost.objects.all()

    if query:
        attachments = attachments.filter(email__icontains=query) | attachments.filter(slots_icontains=query)

    if sort == 'deadline':
        attachments = attachments.order_by('deadline')

    today = timezone.now().date()
    soon_threshold = today + timedelta(days=7)
    for att in attachments:
        att.is_expired = att.application_deadline <= today
        att.is_soon = today < att.application_deadline <= soon_threshold

    paginator = Paginator(attachments, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    own_posts = AttachmentPost.objects.filter(company__user=request.user)
    other_posts = AttachmentPost.objects.exclude(company__user=request.user)

    company = getattr(request.user, 'company', None)
    average_rating = company.reviews.aggregate(avg=Avg('rating'))['avg'] if company else None
    return render(request, 'all_attachment_posts.html', {
        'page_obj': page_obj,
        'query': query,
        'sort': sort,
        'today': timezone.now().date() + timedelta(days=7),
        'own_posts': own_posts,
        'other_posts': other_posts,
        'company': company,
        'average_rating': average_rating or "N/A",
    })

@login_required
def post_house(request):
    if not request.user.has_priviledge(['tenant']):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            house = form.save(commit=False)
            house.posted_by = request.user
            tenant, created = Tenant.objects.get_or_create(
                user=request.user,
                defaults={'name': request.user.get_full_name() or request.user.username}
            )
            house.tenant = tenant
            house.save()

    
            Notification.objects.create(
                recipient=request.user,
                message="Your rental has been posted successfully.",
                link="/dashboard/"  
            )
            return redirect('tenants_dashboard')

    else:
        form = HouseForm()

    return render(request, 'post_house.html', {'form': form})

@login_required
def my_houses(request):
    if not request.user.has_priviledge(['tenant']):
        return HttpResponseForbidden("Only tenants can view their houses.")

    houses = House.objects.filter(tenant__user=request.user)  

    return render(request, 'my_houses.html', {'houses': houses})

@login_required
def edit_house(request, house_id):

    house = get_object_or_404(House, id=house_id, tenant=request.user.tenant)

    if request.method == 'POST':
        form = HouseForm(request.POST, instance=house)
        if form.is_valid():
            form.save()
            return redirect('my_houses')
    else:
        form = HouseForm(instance=house)

    return render(request, 'edit_house.html', {'form': form, 'house': house})

@login_required
def delete_house(request, house_id):

    house =get_object_or_404(House , id=house_id, tenant=request.user.tenant)

    if request.method == 'POST':
        house.delete()
        messages.success(request, "House deleted successfully.")
        return redirect('my_houses')    
    
    return render(request, 'delete_house.html', {'house': house})

@login_required
def submit_house_review(request, house_id):
    house = get_object_or_404(House, id=house_id)

    if request.method == 'POST':
        form = HouseReviewForm(request.POST)
        if form.is_valid():
            review =form.save(commit=False)
            review.user = request.user
            review.house = house
            review.save()
            return redirect('all_houses', house_id=house.id)


    else:
        form =HouseReviewForm()
    return render(request, 'submit_house_review.htnl', {'form': form, 'house': house})

@login_required
def submit_company_review(request, company_id):
    company =get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        form = CompanyReviewForm(request.POST)
        if form.is_valid():
            review =form.save(commit=False)
            review.user = request.user
            review.company = company
            review.save()
            return redirect('all_attachment_posts')

    else:
        form = CompanyReviewForm()

    return render(request, 'submit_company_review.html', {'form': form, 'company': company})

    

@login_required
def view_houses(request):

    houses = House.objects.all().prefetch_related('rooms')

    for house in houses:
        house.available_rooms = house.rooms.filter(is_booked=False).count()
        house.booked_rooms = house.rooms.filter(is_booked=True).count()
        house.total_rooms = house.rooms.count()

    return render(request, 'all_houses.html', {'houses': houses})

@login_required 
def cancel_booking(request, booking_id):
    if not request.user.has_priviledge(['attachee', 'tenant']) and not request.user.is_superuser:
        return HttpResponseForbidden("Only Attachees and Tenants can cancel bookings.")

    booking = get_object_or_404(Booking, id=booking_id)

    is_attachee_booking_owner =(
        hasattr(request.user, 'attachee') and booking.attachee == request.user.attachee
    )
    is_house_wner = (
        hasattr(booking.house_post, 'owner') and booking.house_post.owner == request.user
    )

    if not (is_attachee_booking_owner or is_house_wner or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to cancel this booking.")

    if booking.move_in_date > timezone.now().date():
        booking.status = 'cancelled'
        booking.save()

        if hasattr(booking, 'room') and booking.room:
            booking.room.is_booked = False
            booking.room.save()
                
        messages.success(request, "Booking cancelled successfully")
    else:
        messages.error(request, "Move-in date has passed. Cannot cancel.")

        #Redirect based on the roles
    if request.user.has_priviledge(['attachee']):
        return redirect('my_bookings')
    else:
        return redirect('tenant_house_bookings')
        
@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    user =request.user
    
    is_attachee_owner = hasattr(user, 'attachee') and booking.attachee == user.attachee
    is_tenant_owner = hasattr(user, 'tenant') and  booking.room and booking.room.house.tenant == user
    is_admin = user.is_superuser or user.is_staff

    if not (is_attachee_owner or is_tenant_owner or is_admin):
        return HttpResponseForbidden("you don;t have permission to delete this booking.")
    
    if booking.status != 'cancelled':
        return HttpResponseForbidden("Only cancelled bookings can be deleted.")
    
    booking.delete()
    messages.success(request, "Booking deleted successfully.")

    if is_tenant_owner:
        return redirect('tenant_house_bookings')
    else:
        return redirect('my_bookings')

@login_required
def edit_booking(request, booking_id):
    if not request.user.has_priviledge(['attachee','tenant']):
        return HttpResponseForbidden("You do not have permission to edit this booking.")
    
    booking = get_object_or_404(Booking, id=booking_id)


    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            if hasattr(request.user, 'attachee'):
                return redirect('my_bookings')
            elif hasattr(request.user, 'tenant'):
                return redirect('tenant_house_bookings')
            else:
                return redirect('my_bookings')  


    else:
        form = BookingForm(instance=booking)
    
    if hasattr(request.user, 'tenant'):
        redirect_url = 'tenant_house_bookings'
    
    else:
        redirect_url = 'my_bookings'

    return render(request, 'edit_booking.html', {
        'form': form,
        'booking': booking,
        'redirect_url': redirect_url})

@staff_member_required
def delete_past_bookings(request):
    today = timezone.now().date()

    past_bookings = Booking.objects.filter(move_in_date__lt=today)
    count= past_bookings.count()
    if count > 0:
        past_bookings.delete()
        messages.success(request, f"{count} past bookings deleted successfully.")
    else:
        messages.info(request, "No past bookings to delete.")

    return redirect('my_bookings')

@login_required
def view_attachments(request):
    if not request.user.has_priviledge(['attachee', 'company']):
        return HttpResponseForbidden("Only Attachees and Companies can view attachments.")
        
    return render(request, 'view_attachments.html', {'attachments': AttachmentPost.objects.all()}) 

# companys' Views 
@login_required
def post_attachment(request):
    if not request.user.has_priviledge(['company']):
        return HttpResponseForbidden("Only companies can post attachments.")

    company, _ = Company.objects.get_or_create(
        user=request.user,
        defaults={'name': request.user.get_full_name() or request.user.username}
    )

    if request.method == 'POST':
        form = AttachmentPostForm(request.POST, user=request.user)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.company = company
            attachment.save()
            return redirect('company_dashboard')
    else:
        form = AttachmentPostForm(user=request.user)

    return render(request, 'post_attachment.html', {'form': form})
@login_required
def my_attachment_posts(request):
    if not request.user.has_priviledge(['company']):
        return HttpResponseForbidden()

    my_attachment_posts = AttachmentPost.objects.filter(company__user=request.user)
    
    return render(request, 'my_attachment_posts.html', {
        'my_attachment_posts': my_attachment_posts
    })

@login_required
def edit_attachment(request, attachment_id):
    attachment = get_object_or_404(AttachmentPost, id=attachment_id, company=request.user.company)

    if request.method == 'POST':
        form = AttachmentPostForm(request.POST, instance=attachment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Attachment updated successfully.")
            return redirect('my_attachment_posts')

    else:
        form = AttachmentPostForm(instance=attachment, user=request.user)
    
    return render(request, 'edit_attachment.html', {
        'form': form,
        'attachment': attachment
    })

@login_required
def delete_attachment(request, attachment_id):
    attachment = get_object_or_404(AttachmentPost, id=attachment_id, company__user=request.user)

    if request.method == 'POST':
        attachment.delete()
        messages.success(request, "Attachment deleted successfully.")
        return redirect('company_dashboard')

    return render(request, 'delete_attachment.html', {'attachment': attachment})

def view_applicants(request):
    return render(request, 'view_applicants.html')



# Login views
@login_required
def dashboard_router(request):
    role = request.user.role
    if request.user.is_superuser or request.user.is_staff:
        return redirect('admin_dashboard')
    elif role == 'attachee':
        return redirect('attachee_dashboard')
    elif role == 'company':
        return redirect('company_dashboard')
    elif role == 'tenant':
        return redirect('tenants_dashboard')
    else:
        return redirect(request, 'erro.html', {'message': 'unknown role'})
   
@staff_member_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_dashboard(request):
    users_by_role = CustomUser.objects.values('role').annotate(count=Count('id'))
    booking_count =Booking.objects.count()
    application_count= AttachmentApplication.objects.count()
    tenant_count = Tenant.objects.count()
    attachee_count = Attachee.objects.count()
    company_count = Company.objects.count()

    # Monthly Bookings 
    monthly_bookings =Booking.objects.annotate(month=TruncMonth('created_at')) \
       .values('month').annotate(count=Count('id')).order_by('month')
    
    booking_month_labels = [b['month'].strftime("%b") for b in monthly_bookings]
    booking_month_data = [b['count'] for b in monthly_bookings]

    # Top 5 Compannies by applicant
    top_companies_data = AttachmentApplication.objects.values('attachment_post__company__name')\
        .annotate(application_count=Count('id')).order_by('-application_count')[:5]

    top_company_names  = [item['attachment_post__company__name'] for item in top_companies_data]
    top_company_counts = [item['application_count'] for item in top_companies_data]

    # Top course by applicant count
    course_data = AttachmentApplication.objects.values('attachee__course')\
        .annotate(count=Count('id')).order_by('-count')[:6]

    course_labels =[item['attachee__course'] for item in course_data]
    course_counts = [item['count'] for item in course_data]

    #Pending applications
    pending_apps = AttachmentApplication.objects.filter(status='pending').select_related('attachee', 'company')
    
    # Feedback data
    feedback_count = Feedback.objects.count()
    recent_feedbacks = Feedback.objects.order_by('-submitted_at')[:5]
    # Final context 
    context = {
        'users_by_role': users_by_role,
        'booking_count': booking_count,
        'application_count': application_count,
        'tenant_count': tenant_count,
        'attachee_count': attachee_count,
        'company_count': company_count,
        'booking_month_labels': booking_month_labels,
        'booking_month_data': booking_month_data,
        'top_company_names': top_company_names,
        'top_company_counts': top_company_counts,
        'course_labels': course_labels,
        'course_count': course_counts,
        'pending_apps': pending_apps,
        'feedback_count': feedback_count,
        'recent_feedbacks': recent_feedbacks,
    }
    return render(request, 'dashboards/admin_dashboard.html',context)

@user_passes_test(lambda u: u.is_superuser or u.is_staff)
@login_required
def download_approved_applications_pdf(request):
    approved_apps = AttachmentApplication.objects.filter(status='approved')\
        .select_related('attachee', 'company')

    html_string = render_to_string('pdf/approved_applications.html', {
        'applications': approved_apps,
        'requested_by': request.user,
    })

    try:
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="approved_applications.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Failed to generate PDF: {str(e)}", status=500)

@login_required
def attachee_dashboard(request):
    user = request.user

    if hasattr(user, 'attachee'):
        bookings = Booking.objects.filter(attachee=user.attachee).order_by('-created_at').exclude(status='cancelled')
        applications = AttachmentApplication.objects.filter(attachee=user.attachee).order_by('-start_date')
       
    elif user.is_superuser:
        bookings = Booking.objects.all().order_by('-created_at')
        applications = AttachmentApplication.objects.all().order_by('-start_date')

    else:
        bookings = Booking.objects.none()
        applications = AttachmentApplication.objects.none()

        
    return render(request, 'dashboards/attachee_dashboard.html',{ 
                  'bookings': bookings,
                  'applications': applications,
                  'user': request.user,
                  })



@login_required
def calendar(request):
    user=request.user
    events = [] 

    booking = Booking.objects.filter(user=user, status='approved').first()
    if booking:
        events.append({
            'title': '🏠 House Booking',
            'start': booking.move_in_date.isoformat(),
            'end': booking.move_in_date.isoformat(),
            'color': '#4caf50'
        })

    attachment = AttachmentApplication.objects.filter(attachee=user,status= 'approved')   
    if attachment and hasattr(attachment, 'start_date') and hasattr(attachment, 'end_date'):
         events.append({
            'title': '📄 Attachment Period',
            'start': attachment.start_date.isoformat(),
            'end': attachment.end_date.isoformat(),
            'color': '#2196f3'
         })
    
    return render(request, 'calendar.html', {
        'calendaar_events': json.dumps(events)
    })


@user_passes_test(lambda u:u.is_superuser or u.is_staff)
def mark_as_read(request, notification_id):
    notification =get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    return redirect(notification.data.get('url', '/'))

@login_required
def print_application_letter(request, application_id):
    application = get_object_or_404(AttachmentApplication, id=application_id, attachment=request.user)


    html_content = render_to_string("application_letter.html", {
        'application': application,
        'attachee': application.attachee,
        'company': application.company,
    })
    pdf = HTML(string=html_content).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="application_letter.pdf"'
    return response

@login_required
def send_application_email(request, application_id):
    app = get_object_or_404(AttachmentApplication, id=application_id, attachee=request.user)
    company_email = app.company.email

    html_string = render_to_string('attachee/application_letter.html', {
        'application': app,
        'attachee': app.attachee,
        'company': app.company,
    })

    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as output:
        HTML(string=html_string).write_pdf(output.name)
        output.seek(0) 

        # Create custom subject line
        full_name = app.attachee.get_full_name()
        course = getattr(app.attaachee.attachee, 'course', 'Attachment Program')
        subject = f"Attachment Application - {full_name} ({course})"


        # Create and send email
        email = EmailMessage(
            subject="Attachment Application Letter",
            body=f"Dear {app.company.name},\n\nPlease find attached my application letter for attachment placement.\n\nKind regards,\n{app.attachee.get_full_name()}",
            from_email=request.user.email,
            to=[company_email],
        )
        email.attach("application_letter.pdf", output.read(), 'application/pdf')

         # Try sending and log result
        try:
            email.send()
            app.email_sent = True
            app.email_sent_at = now()
            app.email_error = None
            messages.success(request, "✅ Email successfully sent to the company.")
        except Exception as e:
            app.email_sent = False
            app.email_error = str(e)
            messages.error(request, "❌ Email failed to send. Please try again later.")

        app.save()

    return redirect('attachee-dashboard')


@login_required
def company_dashboard(request):
    return render(request, 'dashboards/company_dashboard.html')
@login_required
def tenants_dashboard(request):
    return render(request, 'dashboards/tenants_dashboard.html')

def submit_feedback(request):
    if request.method == 'POST':
        form =FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
                feedback.is_registered_user = True
                feedback.name = request.user.get_full_name() or request.user.username
                feedback.email = request.user.email
            feedback.save()
            return redirect('contact')
            messages.success(request, "Thank you for your feedback!")

    else:
        form = FeedbackForm()

    return render(request, 'submit_feedback.html', {'form': form})

@staff_member_required
def feedback_list(request):
    feedbacks = Feedback.objects.order_by('-submitted_at')
    return render(request, 'feedback_list.html', {'feedbacks': feedbacks})

@staff_member_required
@require_POST
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.delete()
    messages.success(request, "Feedback deleted successfully.")
    return redirect('feedback_list')

@login_required
def view_booked_rooms(request):
    if not request.user.has_priviledge(['tenant']):
        return HttpResponseForbidden("You have no access to this page.")
    
    tenant = request.user.tenant

    bookings = Booking.objects.filter(
        house_post__tenant=tenant,
        ).select_related('room', 'attachee')

    return render(request, 'view_booked_rooms.html',{'bookings': bookings})

@login_required
def approve_booking(request, booking_id):
    if not request.user.has_priviledge(['tenant']):
        return HttpResponseForbidden("Access denied.")
    
    booking = get_object_or_404(
        Booking, 
        id=booking_id,
        house_post__tenant=request.user.tenant
        )

    if request.method =='POST':
        booking.status = 'approved'
        booking.room.is_booked = True
        booking.room.save()
        booking.save()
        messages.success(request, "Room booking approved successfully.")
        return redirect('view_booked_rooms')

    return redirect('view_booked_rooms')
