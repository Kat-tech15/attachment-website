from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name= 'home'),
    path('about/', views.about, name= 'about'),
    path('contact/', views.contact, name='contact'),
    path('attachments/', views.attachments, name='attachments'),
    path('accomodation/', views.accomodation, name='accomodation'),
    path('attachee/', views.attachee_list, name='attachee_list'),
    path('apply/', views.apply_attachment, name='apply_attachment.html'),
    path('attachments/', views.attachments, name='attachments.html'),
    path('book_house/', views.book_house, name='book_house.html'),
    path('rentals/', views.rentals, name='rentals.html'),
    path('post-attachments/', views.post_attachments, name='post_attachments.html'),
    path('view_attachments/', views.view_attachments, name='view_attachments.html'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/attachee/', views.attachee_dashboard, name='attachee_dashboard'),
    path('dashboard/company/', views.company_dashboard, name='company_dashboard'),
    path('dashboard/tenants/', views.tenant_dashboard, name='tenants_dahsboard'),
    path('login/', views.login, name='login'),

]