from django.urls import path
from . import views

urlpatterns = [
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('feedback_list/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:feedback_id>/delete/', views.delete_feedback, name='delete_feedback'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('announcement_list/', views.announcement_list, name='announcement_list'),
    path('notifications/mark_all_read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
]