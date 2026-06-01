from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import House, Room, Booking
from accounts.models import CustomUser, Tenant
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from .forms import HouseForm, BookingForm

# Create your views here.
@login_required
def post_house(request):
    if not request.user.has_privilege(['tenant']):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            house = form.save(commit=False)
            house.posted_by = request.user
            tenant, created = Tenant.objects.get_or_create(
                user=request.user,
                defaults={'name': request.user.get_full_name() or request.user.username}
            )
            house.tenant = tenant
            house.save()
            messages.success(request, "House posted successfully!", extra_tags="post_house")
            return redirect('post_house')

    else:
        form = HouseForm()

    return render(request, 'post_house.html', {'form': form})

@login_required
def my_houses(request):
    if not request.user.has_privilege(['tenant']):
        return HttpResponseForbidden()

    houses = House.objects.filter(tenant__user=request.user)  

    return render(request, 'my_houses.html', {'houses': houses})

@login_required
def edit_house(request, house_id):

    house = get_object_or_404(House, id=house_id, tenant=request.user.tenant)

    if request.method == 'POST':
        form = HouseForm(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, "House edited successfully.", extra_tags="edit_house")
            return redirect('my_houses')
    else:
        form = HouseForm(instance=house)

    return render(request, 'edit_house.html', {'form': form, 'house': house})

@login_required
def delete_house(request, house_id):

    house =get_object_or_404(House , id=house_id, tenant=request.user.tenant)

    if request.method == 'POST':
        house.delete()
        messages.success(request, "House deleted successfully.", extra_tags="delete_house")
        return redirect('my_houses')    
    
    return render(request, 'delete_house.html', {'house': house})


@login_required
def view_houses(request):

    houses = House.objects.all().prefetch_related('rooms')

    for house in houses:
        house.available_rooms = house.rooms.filter(is_booked=False).count()
        house.booked_rooms = house.rooms.filter(is_booked=True).count()
        house.total_rooms = house.rooms.count()

    return render(request, 'all_houses.html', {'houses': houses})

@login_required 
def cancel_booking(request, booking_id):
    if not request.user.has_privilege(['attachee', 'tenant']) and not request.user.is_superuser:
        return HttpResponseForbidden()

    booking = get_object_or_404(Booking, id=booking_id)

    is_attachee_booking_owner =(
        hasattr(request.user, 'attachee') and booking.attachee == request.user.attachee
    )
    is_house_wner = (
        hasattr(booking.house_post, 'owner') and booking.house_post.owner == request.user
    )

    if not (is_attachee_booking_owner or is_house_wner or request.user.is_superuser):
        return HttpResponseForbidden()

    if booking.move_in_date > timezone.now().date():
        booking.status = 'cancelled'
        booking.save()

        if hasattr(booking, 'room') and booking.room:
            booking.room.is_booked = False
            booking.room.save()
                
        messages.success(request, "Booking cancelled successfully", extra_tags="cancel_booking")
    else:
        messages.error(request, "Move-in date has passed. Cannot cancel.", extra_tags="cancel_booking")

        #Redirect based on the roles
    if request.user.has_privilege(['attachee']):
        return redirect('my_bookings')
    else:
        return redirect('tenant_house_bookings')
        
@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    user =request.user
    
    is_attachee_owner = hasattr(user, 'attachee') and booking.attachee == user.attachee
    is_tenant_owner = hasattr(user, 'tenant') and  booking.room and booking.room.house.tenant == user
    is_admin = user.is_superuser or user.is_staff

    if not (is_attachee_owner or is_tenant_owner or is_admin):
        return HttpResponseForbidden()
    
    if booking.status != 'cancelled':
        return HttpResponseForbidden()
    
    booking.delete()
    messages.success(request, "Booking deleted successfully.", extra_tags="delete_booking")

    if is_tenant_owner:
        return redirect('tenant_house_bookings')
    else:
        return redirect('my_bookings')

@login_required
def edit_booking(request, booking_id):
    if not request.user.has_privilege(['attachee','tenant']):
        return HttpResponseForbidden()
    
    booking = get_object_or_404(Booking, id=booking_id)


    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            if hasattr(request.user, 'attachee'):
                return redirect('my_bookings')
            elif hasattr(request.user, 'tenant'):
                return redirect('tenant_house_bookings')
            else:
                return redirect('my_bookings')  


    else:
        form = BookingForm(instance=booking)
    
    if hasattr(request.user, 'tenant'):
        redirect_url = 'tenant_house_bookings'
    
    else:
        redirect_url = 'my_bookings'

    return render(request, 'edit_booking.html', {
        'form': form,
        'booking': booking,
        'redirect_url': redirect_url})

@staff_member_required
def delete_past_bookings(request):
    today = timezone.now().date()

    past_bookings = Booking.objects.filter(move_in_date__lt=today)
    count= past_bookings.count()
    if count > 0:
        past_bookings.delete()
        messages.success(request, f"{count} past bookings deleted successfully.", extra_tags="delete_past_booking")
    else:
        messages.info(request, "No past bookings to delete.", extra_tags="delete_past_booking")

    return redirect('my_bookings')

@login_required
def my_bookings(request):
    if not request.user.has_privilege(['attachee', 'tenant']) and not request.user.is_superuser:
        return HttpResponseForbidden()
    user = request.user
    today = timezone.now().date()

    if user.is_superuser:
        bookings = Booking.objects.all().select_related('room','house_post', 'attachee')
    elif hasattr(user, 'attachee'):
        bookings = Booking.objects.filter(
            attachee=user.attachee
        ).exclude(
            status='cancelled'
        ).select_related('room', 'house_post', 'attachee')
    else:
        return HttpResponseForbidden()
    
    
    return render(request, 'my_bookings.html', {
        'bookings': bookings,
        'today': today,
    })

# Tenant's Views 
@login_required
def tenant_house_bookings(request):
    if not request.user.has_privilege(['tenant']):
        HttpResponseForbidden()
    
    if request.user.is_superuser:
        bookings = Booking.objects.all().select_related('room', 'attachee')
    else:
        try:
            if hasattr(request.user, 'tenant'):
                tenant= request.user.tenant
                tenant_rooms = Room.objects.filter(house__tenant=tenant)
                bookings = Booking.objects.filter(room__in=tenant_rooms).select_related('room', 'room__house', 'attachee')

            else:
                return HttpResponseForbidden()
        except Room.DoesNotExist:
            bookings = []

    return render(request, 'tenant_house_bookings.html', {
        'bookings': bookings,
        'today': timezone.now().date()
    })

@login_required
def all_houses(request):
    if not request.user.has_privilege(['tenant']):
        return HttpResponseForbidden()

    houses = House.objects.all().prefetch_related('tenant')
    for house in houses:
        house.available_rooms =house.rooms.filter(is_booked=False).count()
        house.booked_rooms = house.rooms.filter(is_booked=True).count()
        house.total_rooms = house.rooms.count()

    return render(request, 'all_houses.html',{'houses': houses})

@receiver(post_save, sender=House)
def create_room(sender, instance, created, **kwargs):
    if created:
        for i in range(1, instance.total_rooms + 1):
            Room.objects.create(
                house=instance,
                room_number=f"{i}",
                price= instance.rent,
                room_type=instance.description)

@login_required
def book_room(request, room_id):
    if not request.user.has_privilege(['tenant','attachee']):
        return HttpResponseForbidden()
    
    

    room = get_object_or_404(Room, id=room_id)
    house = room.house

    if room.is_booked:
        messages.warning(request, "Sorry, this room is already booked.")
        return redirect('all_houses')

    
    attachee = None
    full_name = "Admin"
    phone_number = "N/A"

    
    if request.user.has_privilege(['attachee']) and not request.user.is_superuser:
        attachee = request.user.attachee
        full_name = attachee.full_name
        phone_number = attachee.phone_number
       

    booking = Booking.objects.create(
        attachee=attachee,
        house_post=room.house,
        room=room,
        full_name=full_name,
        phone_number=phone_number,
        move_in_date=timezone.now().date(),
    )
    room.is_booked = True
    room.save()

    messages.success(request, f"Room{room.room_number} booked successfully!", extra_tags="book_room")

    return redirect('house_detail', house_id=house.id)

def house_detail(request, house_id):
    house = get_object_or_404(House, id=house_id)

    rooms = Room.objects.filter(house=house)
    available_rooms = rooms.filter(is_booked=False)
    booked_rooms = rooms.filter(is_booked=True)
    return render(request, 'house_detail.html', {
        'house': house,
        'available_rooms': available_rooms,
        'booked_rooms': booked_rooms,
    })

@login_required
def view_booked_rooms(request):
    if not request.user.has_privilege(['tenant']):
        return HttpResponseForbidden()
    
    tenant = request.user.tenant

    bookings = Booking.objects.filter(
        house_post__tenant=tenant,
        ).select_related('room', 'attachee')

    return render(request, 'view_booked_rooms.html',{'bookings': bookings})

@login_required
def approve_booking(request, booking_id):
    if not request.user.has_privilege(['tenant']):
        return HttpResponseForbidden()
    
    booking = get_object_or_404(
        Booking, 
        id=booking_id,
        house_post__tenant=request.user.tenant
        )

    if request.method =='POST':
        booking.status = 'approved'
        booking.room.is_booked = True
        booking.room.save()
        booking.save()
        messages.success(request, "Room booking approved successfully.", extra_tags="approve_booking")
        return redirect('view_booked_rooms')

    return redirect('view_booked_rooms')