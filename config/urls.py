from django.contrib import admin
from django.urls import path
from coreapp import views

urlpatterns = [
    path('', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', views.dashboard_view, name='dashboard-root'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('businesses/', views.business_list_view, name='business-list'),
    path('branches/', views.branch_list_view, name='branch-list'),
    path('branches/create/', views.branch_create_view, name='branch-create'),
    path('branches/<int:branch_id>/edit/', views.branch_edit_view, name='branch-edit'),
    path('places/', views.place_list_view, name='place-list'),
    path('places/create/', views.place_create_view, name='place-create'),
    path('places/<int:place_id>/edit/', views.place_edit_view, name='place-edit'),
    path('bookings/', views.booking_list_view, name='booking-list'),
]
