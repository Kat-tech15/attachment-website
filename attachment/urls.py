from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name= 'home'),
    path('about/', views.about, name= 'about'),
    path('contact/', views.contact, name='contact'),
    path('attachments/', views.attachments, name='attachments'),
    path('accomodation/', views.accomodation, name='accomodation'),
    path('attachee/', views.attachee_list, name='attachee_list'),
    path('apply/', views.apply_attachment, name='apply_attachment.html')

]