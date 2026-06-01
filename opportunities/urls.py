from django.urls import path
from . import views

urlpatterns = [
    path('my_posts/', views.my_attachment_posts, name='my_attachment_posts'),
    path('attachment/<int:attachment_id>/edit/', views.edit_attachment, name='edit_attachment'),    
    path('attachment/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
    path('post_attachment/', views.post_attachment, name='post_attachment'),
    path('view_attachments/', views.view_attachments, name='view_attachments'),
    path('visited_posts/', views.visited_posts, name='visited_posts'),
    path('all_attachment_posts/', views.all_attachment_posts, name='all_attachment_posts'),
]