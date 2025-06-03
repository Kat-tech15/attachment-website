from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Attachee
from .forms import AttachmentApplicationForm
# Create your views here.
def home(request):
    query = request.GET.get('q')
    if query:
        applications = Attachee.objects.filter(name__icontains=query)
    else:
        applications = Attachee.objects.all()

    return render(request, 'home.html',{'applications': applications})

def about(request):
    return render(request, 'about.html')

def login(request):
    return render(request, 'login.html')

def contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email =request.POST.get('email')
        message = request.POST.get('message')

        contact = ContactMessage.objects.create(
            full_name=full_name,
            email=email,
            message=message,
        )

        contact.save()
        messages.success(request, 'Your message has been sent successfully!')   
        return redirect('contact')

    return render(request, 'contact.html')

def attachments(request):
    return render(request, 'attachments.html')

def accomodation(request):
    return render(request, 'accomodation.html')

def attachee_list(request):
    applications = Attachee.objects.all()
    return render(request, 'attachee_list.html',{'applications': applications})

def apply_attachment(request):
    if request.method == 'POST':
        form = AttachmentApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('application_success')
    else:
        form = AttachmentApplicationForm()
    return render(request, 'apply_attachment.html', {'form': form})
        

def post_attachments(request):
    return render(request, 'post_attachments.html')

def rentals(request):
    return render(request, 'rentals.html')

def book_house(request):
    return render(request, 'book_house.html')

def view_attachments(request):
    return render(request, 'view_attachments.html')

@ login_required
def attachee_dashboard(request):
    return render(request, 'dashboards/attachee_dashboard.html')

@ login_required
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')

@ login_required
def company_dashboard(request):
    return render(request, 'dashboards/company_dashboard.html')


@ login_required
def tenant_dashboard(request):
    return render(request, 'dashboards/tenants_dashboard.html')


def redirect_dashboard(request):
    if request.user is superuser:
        return redirect('admin_dashboard')
    elif hasattr(request.user, 'attacheeprofile'):
        return redirect('attachee_dashboard')
    elif hasattr(request.user, 'companyfrofile'):
        return redirect('company_dashboard')
    elif hasattr(request.user, 'tenantprofile'):
        return redirect('tenant_dashboard')
    else:
        return redirect('login')