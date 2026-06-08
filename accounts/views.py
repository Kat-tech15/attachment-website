from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, Contact, Attachee, Company, Landlord
from .forms import CustomUserCreationForm, EmailLoginForm
from opportunities.models import ApplicationVisit
from notifications.models import Feedback, Testimonials
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
import json
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.urls import reverse
import random
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from housing.models import House, Booking
from opportunities.models import AttachmentPost, ApplicationVisit
from notifications.forms import FeedbackForm

def home(request):
    featured_houses = House.objects.all().order_by('?')[:8]
    recent_attachments = AttachmentPost.objects.order_by('-id')[:6]
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
            messages.success(request, "Thank you for your feedback!", extra_tags="feedback")
            return redirect('/#feedback')
        else:
            form = FeedbackForm()

    return render(request, 'home.html',{
        'form': form,
        'applications': applications,
        'featured_houses': featured_houses,
        'recent_attachments': recent_attachments,
        'testimonials': testimonials
        })

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email is verified
            otp = get_random_string(length=6, allowed_chars='0123456789')
            user.otp = str(otp)
            user.otp_created_at = timezone.now()
            user.save()

            # Send  OTP email
            send_mail(
                'Verify Your Account - OTP',
                f'Hello {user.username},\n\nYour OTP is: {otp}\n\nIt expires in 10 minutes.\n\nIf you did not request this, please ignore this email.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            request.session['email'] = user.email
            messages.info(request, "An OTP has been sent to your email. Please verify your account.", extra_tags="register")
            return redirect('verify_otp')
    else:
        form = CustomUserCreationForm()
    return render(request,'auth/register.html', {'form': form})

def verify_otp(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, "Session expired. Please register again.", extra_tags="verify")
        return redirect('register')
    
    if request.method == 'POST':
        otp_digits = [
            request.POST.get("otp_digit1", ""),
            request.POST.get("otp_digit2", ""),
            request.POST.get("otp_digit3", ""),
            request.POST.get("otp_digit4", ""),
            request.POST.get("otp_digit5", ""),
            request.POST.get("otp_digit6", ""),
        ]
        input_otp = "".join(otp_digits).strip()

        try:
            user = CustomUser.objects.get(email=email)
            # Check if user email is already verified
            if user.email_verified:
                messages.info(request, "Email verified.")
                return redirect('login')
            
            # Check if OTP is correct
            if str(user.otp) != str(input_otp):
                messages.error(request, "Invalid OTP. Please try again.", extra_tags="verify")
                return redirect('verify_otp')
            
            # Check if OTP is expired
            if user.is_otp_expired():
                messages.error(request, "OTP has expired. Please request a new one.", extra_tags="verify")
                return redirect('resend_otp')
            
        # Activate user account
            user.is_active = True
            user.email_verified = True
            user.otp = ''
            user.otp_created_at = None
            user.save()
                
            # Clear the session
            request.session.pop('email', None)

            messages.success(request, "Your account has been verified successfully!", extra_tags="verify")
            return redirect('login')
        
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found. Please register again.", extra_tags="verify")
            return redirect('register')
        
    return render(request, 'auth/verify_otp.html')

def resend_otp(request):
    session_email = request.session.get('email')    

    if request.method == 'POST':
        email = request.POST.get('email') or session_email

        try:
            user = CustomUser.objects.get(email=email)

            if user.email_verified:
                messages.info(request, "Email already verified.")   
                return redirect('login')
            
            # Check if resend is allowed
            if not user.can_resend_otp():
                messages.warning(request, "please wait before requesting for a new OTP.", extra_tags="resend")
                return redirect('verify_otp')
            
            # Generate a  new OTP
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.otp_last_sent = timezone.now()
            user.save()

            send_mail(
                'Verify Your Account - OTP',
                f'Hello {user.username},\n\nYour OTP is: {otp}\n\nIt expires in 10 minutes.\n\nIf you did not request this, please ignore this email.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            request.session['email'] = user.email
            messages.success(request, "An OTP has been sent to your email. Please verify your account.", extra_tags="resend")
            return redirect('verify_otp')
        
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found. Please register again.", extra_tags="resend")
            return redirect('register')
        
    return render(request, 'auth/resend_otp.html')    


def login_view(request):

    if request.method == 'POST':
        form = EmailLoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            remember = request.POST.get('remember')
            if remember:
                request.session.set_expiry(604800)     # 7 days in seconds

            else:
                request.session.set_expiry(0)

            role = user.role
                
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')

            elif role == 'attachee':
                return render(request, 'dashboards/attachee_dashboard.html')

            elif role == 'company':
                return render(request, 'dashboards/company_dashboard.html')

            elif role == 'landlord':
                return render(request, 'dashboards/landlords_dashboard.html')
            else:
                return redirect('home')
        else:
            messages.error(request, "Login failed. Check your credentials and verify your email.", extra_tags="login")

    else:
        form = EmailLoginForm()
    return render(request, 'auth/login.html', {'form': form}) 
    
      
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.', extra_tags="logout")
    return render(request, 'auth/logout.html')



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
        messages.success(request, 'Your message has been sent successfully!', extra_tags="contact")   
        return redirect('contact')

    return render(request, 'contact.html')


@login_required
def dashboard_router(request):
    role = request.user.role

    if request.user.is_superuser or request.user.is_staff:
        return redirect('admin_dashboard')

    elif role == 'attachee':
        return render(request, 'dashboards/attachee_dashboard.html')

    elif role == 'company':
        return render(request, 'dashboards/company_dashboard.html')

    elif role == 'landlord':
        return render(request, 'dashboards/landlords_dashboard.html')

    return render(request, 'error.html', {
        'message': 'Unknown role.'
    })
   
@staff_member_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_dashboard(request):
    users_by_role = CustomUser.objects.values('role').annotate(count=Count('id'))
    users_by_role_json = json.dumps(users_by_role, cls=DjangoJSONEncoder)
    booking_count =Booking.objects.count()
    application_count= ApplicationVisit.objects.count()
    landlord_count = Landlord.objects.count()
    attachee_count = Attachee.objects.count()
    company_count = Company.objects.count()

    # Monthly Bookings 
    monthly_bookings =Booking.objects.annotate(month=TruncMonth('created_at')) \
       .values('month').annotate(count=Count('id')).order_by('month')
    
    booking_month_labels = [b['month'].strftime("%b") for b in monthly_bookings]
    booking_month_data = [b['count'] for b in monthly_bookings]

    # Top 5 Compannies by applicant
    top_companies_data = ApplicationVisit.objects.values('attachment_post__company__name')\
        .annotate(application_count=Count('id')).order_by('-application_count')[:5]

    top_company_names  = [item['attachment_post__company__name'] for item in top_companies_data]
    top_company_counts = [item['application_count'] for item in top_companies_data]

    course_data = ApplicationVisit.objects.values('course__name')\
        .annotate(count=Count('id')).order_by('-count')

    course_labels = [c['course__name'] for c in course_data]    
    course_count = [c['count'] for c in course_data]
    feedback_count = Feedback.objects.count()
    recent_feedbacks = Feedback.objects.order_by('-submitted_at')[:5]
    context = {
        'users_by_role_json': users_by_role_json,
        'booking_count': booking_count,
        'application_count': application_count,
        'landlord_count': landlord_count,
        'attachee_count': attachee_count,
        'company_count': company_count,
        'booking_month_labels': json.dumps(booking_month_labels),
        'booking_month_data': json.dumps(booking_month_data),
        'top_company_names': json.dumps(top_company_names),
        'top_company_counts': json.dumps(top_company_counts),
        'course_labels': json.dumps(course_labels),
        'course_count': json.dumps(course_count),
        'feedback_count': feedback_count,
        'recent_feedbacks': recent_feedbacks,
    }
    return render(request, 'dashboards/admin_dashboard.html',context)


@login_required
def attachee_dashboard(request):

    user = request.user
    attachee = getattr(user, "attachee", None)

    if not attachee:
        messages.error(request, "Attachee profile not found.")
        return redirect("home")

    # Base querysets (single source of truth)
    bookings_qs = Booking.objects.filter(
        attachee=attachee,
    ).exclude(
        status="cancelled"
    )

    applications_qs = ApplicationVisit.objects.filter(
        attachee=attachee
    )

    context = {
        # recent items (for dashboard preview)
        "bookings": bookings_qs.order_by("-id")[:5],
        "applications": applications_qs.order_by("-id")[:5],

        # stats
        "booking_count": bookings_qs.count(),
        "application_count": applications_qs.count(),

        "pending_applications": applications_qs.filter(status="pending").count(),
        "accepted_applications": applications_qs.filter(status="accepted").count(),

        "user": user,
    }

    return render(request, "dashboards/attachee_dashboard.html", context)

@login_required
def company_dashboard(request):

    company = Company.objects.get(user=request.user)
    
    if not company:
        messages.error(request, "Company profile not found.")
        return redirect('home')

    today = timezone.now().date()

    # Base queryset (single source of truth)
    posts = AttachmentPost.objects.filter(company=company).order_by('-created_at')

    # Derived metrics (REAL-TIME)
    attachment_count = posts.count()
    my_posts_count = posts.count()

    applications_count = ApplicationVisit.objects.filter(
        attachment_post__company=company
    ).count()

    # "Active" = not expired
    active_listings = posts.filter(
        application_deadline__gte=today
    ).count()

    # Recent posts
    my_posts = posts[:5]

    # Most viewed post (optional but useful)
    most_viewed_post = (
        posts.annotate(vcount=Count('applicationvisit'))
        .order_by('-vcount')
        .first()
    )

    # Engagement rate (safe calculation)
    total_visits = applications_count
    engagement_rate = f"{min(total_visits * 2, 100)}%"

    context = {
        "attachment_count": attachment_count,
        "my_posts_count": my_posts_count,
        "applications_count": applications_count,
        "active_listings": active_listings,

        "my_posts": my_posts,
        "most_viewed_post": most_viewed_post,

        "engagement_rate": engagement_rate,
    }

    return render(request, "dashboards/company_dashboard.html", context)

@login_required
def landlords_dashboard(request):

    landlord = getattr(request.user, 'landlord', None)

    if not landlord:
        messages.error(request, "Landlord profile not found.")
        return redirect('home')

    bookings = Booking.objects.filter(
        house_post__landlord=landlord
    ).select_related('house_post').order_by('-created_at')

    houses = House.objects.filter(landlord=landlord)

    context = {
        "booking_count": bookings.count(),
        "house_count": houses.count(),

        # IMPORTANT: normalize status checks
        "active_booking_count": bookings.filter(status='approaved').count(),
        "pending_bookings": bookings.filter(status='pending').count(),

        "recent_bookings": list(bookings[:5]),
    }

    return render(request, "dashboards/landlords_dashboard.html", context)