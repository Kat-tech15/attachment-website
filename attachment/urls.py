from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


class CustomPasswordResetView(auth_views.PasswordResetView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = 'attachment-website-production.up.railway.app'
        return context
    
urlpatterns = [
    path('', views.home, name= 'home'),
    path('attachee/', views.attachee_list, name='attachee_list'),
    path('view_attachments/', views.view_attachments, name='view_attachments'),
    path('visited_posts/', views.visited_posts, name='visited_posts'),
    path('book_room/<int:room_id>/', views.book_room, name='book_room'),
    path('all_houses/', views.all_houses, name='all_houses'),
    path('all_attachment_posts/', views.all_attachment_posts, name='all_attachment_posts'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/attachee/', views.attachee_dashboard, name='attachee_dashboard'),
    path('dashboard/company/', views.company_dashboard, name='company_dashboard'),
    path('dashboard/tenants/', views.tenants_dashboard, name='tenants_dashboard'),
    path('register/', views.register_view, name='register'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url='/password_reset/done/',
             extra_context={
                'domain': 'attachment-website-production.up.railway.app',
                'protocol': 'https',
            }
        ),name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('dashboard/', views.dashboard_router, name='dashboard'),
    path('post_house/', views.post_house, name='post_house'),
    path('my_houses/', views.my_houses, name='my_houses'),
    path('house/<int:house_id>/', views.house_detail, name='house_detail'),
    path('house/<int:house_id>/edit/', views.edit_house, name='edit_house'),
    path('house/<int:house_id>/delete/', views.delete_house, name='delete_house'),
    path('view_houses/', views.view_houses, name='view_houses'),
    path('my_posts/', views.my_attachment_posts, name='my_attachment_posts'),
    path('attachment/<int:attachment_id>/edit/', views.edit_attachment, name='edit_attachment'),    
    path('attachment/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
    path('post_attachment/', views.post_attachment, name='post_attachment'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('my_bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('feedback_list/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:feedback_id>/delete/', views.delete_feedback, name='delete_feedback'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    path('bookings/delete-past/', views.delete_past_bookings, name='delete_past_bookings'),
    path('bookings/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('booking/<int:booking_id>/approve', views.approve_booking, name='approve_booking'),
    path('view_ booked_rooms/', views.view_booked_rooms, name='view_booked_rooms'),
    path('tenant/bookings', views.tenant_house_bookings, name='tenant_house_bookings'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/mark_all_read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    ]