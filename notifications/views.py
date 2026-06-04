from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Notification, Announcement, Feedback
from .forms import FeedbackForm
from accounts.models import CustomUser  
from django.views.decorators.http import require_POST



@user_passes_test(lambda u:u.is_superuser or u.is_staff)
def mark_as_read(request, notification_id):
    notification =get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    return redirect(notification.data.get('url', '/'))

@login_required
def company_dashboard(request):
    return render(request, 'dashboards/company_dashboard.html')
@login_required
def landlords_dashboard(request):
    return render(request, 'dashboards/landlords_dashboard.html')

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
            return redirect('feedback')
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
    messages.success(request, "Feedback deleted successfully.", extra_tags="delete_feedback")
    return redirect('feedback_list')

@staff_member_required
def post_announcement(request):
    if request.method == 'POST':
        text = request.POST.get('announcement')

        for user in CustomUser.objects.exclude(is_superuser):
           Notification.objects.create(
               recipient=user,
               message=f"New Announcement: {text}",
               url='/dashboard/'
           )
        messages.success(request, "Announcement sent successfully.", extra_tags="announcement")
        return redirect('admin_dashboard')

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notification_list.html', {'notifications': notifications})

@login_required
def mark_all_notifications_as_read(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    notifications.update(is_read=True)
    messages.success(request, "All notifications marked as read.", extra_tags="announcement")
    return HttpResponseRedirect(reverse('notification_list'))

def announcement_list(request):
    announcements = Announcement.objects.order_by('-created_at')
    return render(request, 'announcement_list.html', {'announcements': announcements})