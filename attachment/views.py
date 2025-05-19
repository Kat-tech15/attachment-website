from django.shortcuts import render,redirect,get_object_or_404
from .models import AttacheeInfo
from .forms import AttachmentApplicationForm
# Create your views here.
def home(request):
    query = request.GET.get('q')
    if query:
        applications = AttacheeInfo.objects.filter(full_name__icontains=query)
    else:
        applications = AttacheeInfo.objects.all()

    return render(request, 'home.html',{'appplications': applications})

def about(request):
    return render(request, 'about.html')

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
    applications = AttacheeInfo.objects.all()
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
        