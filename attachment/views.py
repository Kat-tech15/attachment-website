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
from django.dispatch import receiver
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms  import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate , get_user_model 
from django.http import HttpResponseForbidden, HttpResponse
from .models import CustomUser, Attachee, Company, House, AttachmentApplication, Booking, AttachmentPost,Company,Contact, RentalListing, Room, Notification, Tenant
from .forms import CustomUserCreationForm,HouseForm
from django.contrib import messages
from django.utils import timezone
from .forms import AttachmentPostForm, HouseForm, AttachmentApplicationForm, HouseReviewForm, CompanyReviewForm

# Create your views here.



user = get_user_model()
is_superuser = True
is_staff =True


def home(request):
    featured_houses = House.objects.all().order_by('?')[:3]
    recent_attachments = AttachmentPost.objects.order_by('-id')[:2]
    query = request.GET.get('q')
    if query:
        applications = Attachee.objects.filter(name__icontains=query)
    else:
        applications = Attachee.objects.all()

    return render(request, 'home.html',{
        'applications': applications,
        'featured_houses': featured_houses,
        'recent_attachments': recent_attachments
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


@login_required
def book_rental(request, rental_id):
    if  not request.user.has_priviledge(['attachee']):
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
    if not request.user.has_priviledge(['attachee', 'tenant']):
        return HttpResponseForbidden("Only Attachees and Tenants can view bookings.")

    bookings = Booking.objects.filter(attachee=request.user).select_related('house')
    return render(request, 'my_bookings.html', {'bookings': bookings})

# Tenant's Views 

@login_required
def all_rentals(request):
    if not request.user.has_priviledge(['tenant']):
        return HttpResponseForbidden()

    rentals = RentalListing.objects.all().prefetch_related('rooms', 'reviews').annotate(
        avg_rating = Avg('reviews__rating')
    )

    for rental in rentals:
        rental.available_rooms =rental.rooms.filter(is_booked=False).count()
        rental.ooked_rooms = rental.rooms.filter(is_booked=True).count()
        rental.total_rooms = rental.rooms.count()

    return render(request, 'all_rentals.html',{'rentals': rentals})

@receiver(post_save, sender=RentalListing)
def create_room(sender, instance, created, **kwargs):
    if created:
        for i in range(1, instance.total_rooms + 1):
            Room.objects.create(rental=instance, room_number=f"Room {i}")

def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    rental = room.rental

    if room.is_booked:
        messages.warning(request, "Sorry, this room is already booked.")
        return redirect('all_rentals')
    
    booking = Booking.objects.create(
        attachee=request.user.attachee,
        rental_post=room.house,
        full_name=request.user.attachee.full_name,
        contact=request.user.attachee.phone_number
    )
    room.is_booked = True
    room.save()
    messages.success(request, f"Room {room.room_number} booked successfully!")

    return render(request, 'book_room.html', {
        'room': room,
        'booking': booking
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
def post_rental(request):
    if not request.user.has_priviledge(['tenant']):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            house = form.save(commit=False)
            house.posted_by = request.user
            tenant, created = Tenant.objects.get_or_create(
                user=request.user,
                defaults={'full_name': request.user.get_full_name() or request.user.username}
            )
            house.tenant = tenant
            house.save()

    
            notify.send(
                sender=request.user,
                recipient=house.tenant,
                verb='Your rental has been posted successfully',
                )
            return redirect('tenants_dashboard')

    else:
        form = HouseForm()

    return render(request, 'post_rental.html', {'form': form})

def make_inquiry(request):
    return render(request, 'make_inquiry.html')

@login_required
def submit_house_review(request, rental_id):
    rental = get_object_or_404(RentalListing, id=rental_id)

    if request.method == 'POST':
        form = HouseReviewForm(request.POST)
        if form.is_valid():
            review =form.save(commit=False)
            review.user = request.user
            review.rental = rental
            review.save()
            return redirect('all_rentals', rental_id= rental.id)


    else:
        form =HouseReviewForm()
    return render(request, 'submit_house_review.htnl', {'form': form, 'rental': rental})

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
def view_rentals(request):
    rentals = RentalListing.objects.all().prefetch_related('rooms', 'reviews').annotate(
        avg_rating=Avg('reviews__rating')
    )

    for rental in rentals:
        rental.available_rooms = rental.rooms.filter(is_booked=False).count()
        rental.booked_rooms = rental.rooms.filter(is_booked=True).count()
        rental.total_rooms = rental.rooms.count()

    return render(request, 'all_rentals.html', {'rentals': rentals})


def view_attachments(request):
    return render(request, 'view_attachments.html', {'attachments': AttachmentPost.objects.all()}) 

# companys' Views 
@login_required 
def post_attachment(request):
    if not request.user.has_priviledge(['company']):
        return HttpResponseForbidden("You have no permission to post attachments.")

    if user.is_superuser or user.is_staff:
        pass

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
            return redirect('company_dashboard')
        
    else:
        form = AttachmentPostForm(user=request.user)

    return render(request, 'post_attachment.html', {'form': form})

def my_attachment_posts(request):
    if not request.user.has_priviledge(['company']):
        return HttpResponseForbidden()

    my_attachment_posts = AttachmentPost.objects.filter(company__user=request.user)
    
    return render(request, 'my_attachment_posts.html', {
        'my_attachment_posts': my_attachment_posts
    })
 
def view_applicants(request):
    return render(request, 'view_applicants.html')

# Login views
@login_required
def dashboard_router(request):
    role = request.user.role
    if user.is_superuser or user.is_staff:
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

    context = {
        'users_by_role': users_by_role,
        'booking_count': booking_count,
        'application_count': application_count,
    }
    monthly_bookings =Booking.objects.annotate(month=TruncMonth('created_at')) \
       .values('month')\
       .annotate(count=Count('id'))\
        .order_by('month')
    
    labels = [b['month'].strftime("%b") for b in monthly_bookings]
    data = [b['count'] for b in monthly_bookings]

    context = {
        'booking_month_labels': labels,
        'booking_month_data': data,
    }
    top_companies_data = AttachmentApplication.objects.values('attachment_post__company__name')\
        .annotate(application_count=Count('id'))\
        .order_by('-application_count')[:5]

    top_company_names  = [item['attachment_post__company__name'] for item in top_companies_data]
    top_company_counts = [item['application_count'] for item in top_companies_data]

    context.update({
        'top_company_names': top_company_names,
        'top_company_counts': top_company_counts,
    })

    course_data = AttachmentApplication.objects.values('attachee__course')\
        .annotate(count=Count('id')).order_by('-count')[:6]

    course_labels =[item['attachee__course'] for item in course_data]
    course_counts = [item['count'] for item in course_data]

    context.update({
        'course_labels': course_labels,
        'course_count': course_counts,
    })

    pending_apps = AttachmentApplication.objects.filter(status='pending').select_related('attachee', 'company')

    context.update({
        'pending_apps': pending_apps,
    })

    return render(request, 'dashboards/admin_dashboard.html')

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
    if request.user.is_superuser:
            
        bookings = Booking.objects.all().order_by('-created_at')
        applications = AttachmentApplication.objects.all().order_by('-start_date')
    else:
        try:
            attachee = Attachee.objects.get(user=request.user)
        except Attachee.DoesNotExist:
            messages.error(request, "Complete your profile first.")
            return redirect('register') 
         
        bookings = Booking.objects.filter(attachee=attachee).order_by('-created_at')
        applications = AttachmentApplication.objects.filter(attachee=attachee).order_by('-start_date')

        
    return render(request, 'dashboards/attachee_dashboard.html',{ 
                  'bookings': bookings,
                  'applications': applications,
                  'today': timezone.now().date()
                  })

@login_required 
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, User=request.user)

    if booking.move_in_date > timezone.now.date():
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking cancelled succssfully.")
    
    else:
        messages.error(request, "Move-in date has passed. Cannot cancel.")

    return redirect('my_bookings')

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

