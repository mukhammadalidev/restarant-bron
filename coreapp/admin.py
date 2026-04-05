from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Customer, Business, BusinessStaff, Branch, Place, Booking, ProductCategory, Product


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ['id', 'telegram_id', 'full_name', 'username', 'created_at']
    search_fields = ['full_name', 'username', 'telegram_id']


@admin.register(Business)
class BusinessAdmin(ModelAdmin):
    list_display = ['id', 'name', 'business_type', 'phone', 'address', 'is_active']
    list_filter = ['business_type', 'is_active']
    search_fields = ['name', 'phone', 'address']


@admin.register(BusinessStaff)
class BusinessStaffAdmin(ModelAdmin):
    list_display = ['id', 'user', 'business', 'role', 'telegram_id', 'is_active']
    list_filter = ['role', 'is_active', 'business']
    search_fields = ['user__username', 'business__name', 'telegram_id']


@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ['id', 'name', 'business', 'address', 'open_time', 'close_time', 'is_active']
    list_filter = ['business', 'is_active']
    search_fields = ['name', 'address']


@admin.register(Place)
class PlaceAdmin(ModelAdmin):
    list_display = ['id', 'name', 'branch', 'place_type', 'capacity', 'price', 'is_active']
    list_filter = ['place_type', 'is_active', 'branch__business']
    search_fields = ['name', 'description']


@admin.register(Booking)
class BookingAdmin(ModelAdmin):
    list_display = ['id', 'booking_code', 'customer', 'business', 'branch', 'place', 'booking_date', 'status']
    list_filter = ['status', 'business', 'booking_date']
    search_fields = ['booking_code', 'customer__full_name']


@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ['id', 'name', 'business']
    list_filter = ['business']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['id', 'name', 'business', 'category', 'price', 'is_available']
    list_filter = ['business', 'category', 'is_available']
    search_fields = ['name']