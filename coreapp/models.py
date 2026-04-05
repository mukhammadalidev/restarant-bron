from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

class Customer(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return self.full_name or str(self.telegram_id)

class Business(models.Model):
    TYPE_CHOICES = (('restaurant', 'Restaurant'), ('hall', 'Wedding Hall'), ('cafe', 'Cafe'))
    name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class BusinessStaff(models.Model):
    ROLE_CHOICES = (('owner', 'Owner'), ('manager', 'Manager'), ('staff', 'Staff'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_staff')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='staff_members')
    telegram_id = models.BigIntegerField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    class Meta:
        unique_together = ('user', 'business')
    def __str__(self):
        return f"{self.business.name} | {self.user.username} | {self.role}"

class Branch(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.business.name} | {self.name}"

class Place(models.Model):
    TYPE_CHOICES = (('table','Table'),('vip_room','VIP Room'),('hall','Hall'),('cabin','Cabin'))
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=255)
    place_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='table')
    capacity = models.PositiveIntegerField(default=4)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.branch.name} | {self.name}"

class Booking(models.Model):
    STATUS_CHOICES = (('pending','Pending'),('confirmed','Confirmed'),('rejected','Rejected'),('cancelled','Cancelled'))
    booking_code = models.CharField(max_length=64, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='bookings')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='bookings')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    guests_count = models.PositiveIntegerField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def clean(self):
        if self.branch.business_id != self.business_id:
            raise ValidationError("Branch tanlangan businessga tegishli emas.")
        if self.place.branch_id != self.branch_id:
            raise ValidationError("Place tanlangan branchga tegishli emas.")
        if self.end_time <= self.start_time:
            raise ValidationError("Tugash vaqti boshlanishdan katta bo'lishi kerak.")
        if self.guests_count > self.place.capacity:
            raise ValidationError("Guests soni place capacitydan katta.")
        qs = Booking.objects.filter(place=self.place, booking_date=self.booking_date, status__in=['pending','confirmed']).exclude(pk=self.pk)
        for item in qs:
            if self.start_time < item.end_time and item.start_time < self.end_time:
                raise ValidationError("Bu joy shu vaqt oralig'ida band.")
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    def __str__(self):
        return self.booking_code





class ProductCategory(models.Model):
    # Restoran menyusi uchun kategoriya
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.business.name} | {self.name}"


class Product(models.Model):
    # Mening taomlarim shu yerda saqlanadi
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.business.name} | {self.name}"