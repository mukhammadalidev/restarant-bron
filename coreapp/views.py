from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import BranchForm, PlaceForm
from .models import Business, BusinessStaff, Branch, Place, Booking

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Login yoki parol noto'g'ri.")
    return render(request, 'coreapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def allowed_businesses(user):
    if user.is_superuser:
        return Business.objects.all()
    return Business.objects.filter(staff_members__user=user, staff_members__is_active=True).distinct()

@login_required
def dashboard_view(request):
    businesses = allowed_businesses(request.user)
    stats = {
        'business_count': businesses.count(),
        'branch_count': Branch.objects.filter(business__in=businesses).count(),
        'place_count': Place.objects.filter(branch__business__in=businesses).count(),
        'booking_count': Booking.objects.filter(business__in=businesses).count(),
        'pending_count': Booking.objects.filter(business__in=businesses, status='pending').count(),
    }
    return render(request, 'coreapp/dashboard.html', {'stats': stats})

@login_required
def business_list_view(request):
    return render(request, 'coreapp/business_list.html', {'businesses': allowed_businesses(request.user)})

@login_required
def branch_list_view(request):
    branches = Branch.objects.filter(business__in=allowed_businesses(request.user)).select_related('business')
    return render(request, 'coreapp/branch_list.html', {'branches': branches})

@login_required
def branch_create_view(request):
    form = BranchForm(request.POST or None)
    form.fields['business'].queryset = allowed_businesses(request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Filial yaratildi.')
        return redirect('branch-list')
    return render(request, 'coreapp/branch_form.html', {'form': form, 'title': 'Filial yaratish'})

@login_required
def branch_edit_view(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id, business__in=allowed_businesses(request.user))
    form = BranchForm(request.POST or None, instance=branch)
    form.fields['business'].queryset = allowed_businesses(request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Filial yangilandi.')
        return redirect('branch-list')
    return render(request, 'coreapp/branch_form.html', {'form': form, 'title': 'Filial tahrirlash'})

@login_required
def place_list_view(request):
    places = Place.objects.filter(branch__business__in=allowed_businesses(request.user)).select_related('branch', 'branch__business')
    return render(request, 'coreapp/place_list.html', {'places': places})

@login_required
def place_create_view(request):
    form = PlaceForm(request.POST or None)
    form.fields['branch'].queryset = Branch.objects.filter(business__in=allowed_businesses(request.user))
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Joy yaratildi.')
        return redirect('place-list')
    return render(request, 'coreapp/place_form.html', {'form': form, 'title': 'Joy yaratish'})

@login_required
def place_edit_view(request, place_id):
    place = get_object_or_404(Place, id=place_id, branch__business__in=allowed_businesses(request.user))
    form = PlaceForm(request.POST or None, instance=place)
    form.fields['branch'].queryset = Branch.objects.filter(business__in=allowed_businesses(request.user))
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Joy yangilandi.')
        return redirect('place-list')
    return render(request, 'coreapp/place_form.html', {'form': form, 'title': 'Joy tahrirlash'})

@login_required
def booking_list_view(request):
    bookings = Booking.objects.filter(business__in=allowed_businesses(request.user)).select_related('customer','business','branch','place').order_by('-created_at')
    return render(request, 'coreapp/booking_list.html', {'bookings': bookings})
