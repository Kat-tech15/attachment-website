from django.urls import path
from . import views 


urlpatterns = [
    path('post_house/', views.post_house, name='post_house'),
    path('my_houses/', views.my_houses, name='my_houses'),
    path('house/<int:house_id>/', views.house_detail, name='house_detail'),
    path('house/<int:house_id>/edit/', views.edit_house, name='edit_house'),
    path('house/<int:house_id>/delete/', views.delete_house, name='delete_house'),
    path('view_houses/', views.view_houses, name='view_houses'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('my_bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    path('bookings/delete-past/', views.delete_past_bookings, name='delete_past_bookings'),
    path('bookings/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('booking/<int:booking_id>/approve', views.approve_booking, name='approve_booking'),
    path('view_ booked_rooms/', views.view_booked_rooms, name='view_booked_rooms'),
    path('landlord/bookings', views.landlord_house_bookings, name='landlord_house_bookings'),
    path('book_room/<int:room_id>/', views.book_room, name='book_room'),
    path('all_houses/', views.all_houses, name='all_houses'),
]