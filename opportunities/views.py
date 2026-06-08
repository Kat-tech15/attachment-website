from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Company, AttachmentPost, ApplicationVisit
from accounts.models import Attachee
from .forms import AttachmentPostForm
from django.core.paginator import Paginator
from django.db.models import Avg  
from django.contrib import messages  
from django.http import HttpResponseForbidden

@login_required
def all_attachment_posts(request):
    if not request.user.has_privilege(['company', 'attachee']):
        return HttpResponseForbidden()
    
    query = request.GET.get('q')
    sort = request.GET.get('sort')

    attachments = AttachmentPost.objects.all()

    if query:
        attachments = attachments.filter(email__icontains=query) | attachments.filter(slots__icontains=query)

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
    return render(request, 'company/all_attachment_posts.html', {
        'page_obj': page_obj,
        'query': query,
        'sort': sort,
        'today': timezone.now().date() + timedelta(days=7),
        'own_posts': own_posts,
        'other_posts': other_posts,
        'company': company,
        'average_rating': average_rating or "N/A",
    })


def view_attachments(request):
    if not request.user.has_privilege(['attachee', 'company']):
        return HttpResponseForbidden()
        
    return render(request, 'company/view_attachments.html', {'attachments': AttachmentPost.objects.all()}) 

 
@login_required
def post_attachment(request):
    if not request.user.has_privilege(['company']):
        return HttpResponseForbidden()

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

    return render(request, 'company/post_attachment.html', {'form': form})


@login_required
def my_attachment_posts(request):
    if not request.user.has_privilege(['company']):
        return HttpResponseForbidden()

    my_attachment_posts = AttachmentPost.objects.filter(company__user=request.user)
    
    return render(request, 'company/my_attachment_posts.html', {
        'my_attachment_posts': my_attachment_posts
    })

@login_required
def edit_attachment(request, attachment_id):
    attachment = get_object_or_404(AttachmentPost, id=attachment_id, company=request.user.company)

    if request.method == 'POST':
        form = AttachmentPostForm(request.POST, instance=attachment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Attachment updated successfully.", extra_tags="edit_attachment")
            return redirect('my_attachment_posts')

    else:
        form = AttachmentPostForm(instance=attachment, user=request.user)
    
    return render(request, 'company/edit_attachment.html', {
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

    return render(request, 'company/delete_attachment.html', {'attachment': attachment})

def visited_posts(request):
    if not request.user.has_privilege(['attachee']):
        return HttpResponseForbidden()
    
    attachee = request.user
    visits = ApplicationVisit.objects.filter(attachee=attachee).select_related('attachment_post__company')
    return render(request, 'company/visited_posts.html', {'visits': visits})

def attachee_list(request):
    applications = Attachee.objects.all()
    return render(request, 'attachee_list.html',{'applications': applications})