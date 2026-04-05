from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from coreapp.models import (
    Business,
    BusinessStaff,
    Branch,
    Place,
    ProductCategory,
    Product,
)


class Command(BaseCommand):
    help = "Demo data yaratish"

    def handle(self, *args, **kwargs):
        # =========================
        # USERS
        # =========================
        admin, created = User.objects.get_or_create(username="admin")
        if created:
            admin.set_password("admin12345")
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
        else:
            admin.set_password("admin12345")
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()

        owner, created = User.objects.get_or_create(username="owner1")
        if created:
            owner.set_password("admin12345")
            owner.is_staff = True
            owner.save()
        else:
            owner.set_password("admin12345")
            owner.is_staff = True
            owner.save()

        manager, created = User.objects.get_or_create(username="manager1")
        if created:
            manager.set_password("admin12345")
            manager.is_staff = True
            manager.save()
        else:
            manager.set_password("admin12345")
            manager.is_staff = True
            manager.save()

        # =========================
        # BUSINESSES
        # =========================
        grand, _ = Business.objects.get_or_create(
            name="Grand Restaurant",
            defaults={
                "business_type": "restaurant",
                "description": "Oilaviy restoran",
                "phone": "+998901111111",
                "address": "Buxoro markaz",
                "is_active": True,
            },
        )

        royal, _ = Business.objects.get_or_create(
            name="Royal Toyxona",
            defaults={
                "business_type": "hall",
                "description": "Toy va tadbir zali",
                "phone": "+998902222222",
                "address": "Buxoro shahar",
                "is_active": True,
            },
        )

        # =========================
        # STAFF
        # =========================
        BusinessStaff.objects.get_or_create(
            user=owner,
            business=grand,
            defaults={
                "telegram_id": 7420585147,
                "role": "owner",
                "is_active": True,
            },
        )

        BusinessStaff.objects.get_or_create(
            user=manager,
            business=grand,
            defaults={
                "telegram_id": 7420585147,
                "role": "manager",
                "is_active": True,
            },
        )

        BusinessStaff.objects.get_or_create(
            user=owner,
            business=royal,
            defaults={
                "telegram_id": 7420585147,
                "role": "owner",
                "is_active": True,
            },
        )

        # =========================
        # BRANCHES
        # =========================
        b1, _ = Branch.objects.get_or_create(
            business=grand,
            name="Grand Main Branch",
            defaults={
                "address": "Buxoro markaz",
                "open_time": "09:00",
                "close_time": "23:00",
                "is_active": True,
            },
        )

        b2, _ = Branch.objects.get_or_create(
            business=grand,
            name="Grand Kogon Branch",
            defaults={
                "address": "Kogon shahar",
                "open_time": "10:00",
                "close_time": "22:00",
                "is_active": True,
            },
        )

        b3, _ = Branch.objects.get_or_create(
            business=royal,
            name="Royal Main Hall",
            defaults={
                "address": "Buxoro shahar",
                "open_time": "09:00",
                "close_time": "23:30",
                "is_active": True,
            },
        )

        # =========================
        # PLACES
        # =========================
        Place.objects.get_or_create(
            branch=b1,
            name="Stol 1",
            defaults={
                "place_type": "table",
                "capacity": 4,
                "price": 100000,
                "description": "Kichik stol",
                "is_active": True,
            },
        )

        Place.objects.get_or_create(
            branch=b1,
            name="VIP 1",
            defaults={
                "place_type": "vip_room",
                "capacity": 8,
                "price": 300000,
                "description": "VIP xona",
                "is_active": True,
            },
        )

        Place.objects.get_or_create(
            branch=b2,
            name="Stol 5",
            defaults={
                "place_type": "table",
                "capacity": 6,
                "price": 150000,
                "description": "Katta stol",
                "is_active": True,
            },
        )

        Place.objects.get_or_create(
            branch=b3,
            name="Zal A",
            defaults={
                "place_type": "hall",
                "capacity": 120,
                "price": 4000000,
                "description": "Katta banket zali",
                "is_active": True,
            },
        )

        # =========================
        # MENU - GRAND
        # =========================
        grand_cat_main, _ = ProductCategory.objects.get_or_create(
            business=grand,
            name="Asosiy taomlar",
        )

        grand_cat_drink, _ = ProductCategory.objects.get_or_create(
            business=grand,
            name="Ichimliklar",
        )

        Product.objects.get_or_create(
            business=grand,
            category=grand_cat_main,
            name="Osh",
            defaults={
                "price": 35000,
                "description": "An'anaviy o'zbek osh",
                "is_available": True,
            },
        )

        Product.objects.get_or_create(
            business=grand,
            category=grand_cat_main,
            name="Shashlik",
            defaults={
                "price": 25000,
                "description": "Mol go'shti shashlik",
                "is_available": True,
            },
        )

        Product.objects.get_or_create(
            business=grand,
            category=grand_cat_drink,
            name="Coca Cola",
            defaults={
                "price": 15000,
                "description": "Sovuq ichimlik",
                "is_available": True,
            },
        )

        Product.objects.get_or_create(
            business=grand,
            category=grand_cat_drink,
            name="Fanta",
            defaults={
                "price": 15000,
                "description": "Gazli ichimlik",
                "is_available": True,
            },
        )

        Product.objects.get_or_create(
            business=grand,
            category=grand_cat_drink,
            name="Choy",
            defaults={
                "price": 5000,
                "description": "Qora choy",
                "is_available": True,
            },
        )

        # =========================
        # MENU - ROYAL
        # =========================
        royal_cat, _ = ProductCategory.objects.get_or_create(
            business=royal,
            name="Banket menyu",
        )

        Product.objects.get_or_create(
            business=royal,
            category=royal_cat,
            name="Banket Set",
            defaults={
                "price": 120000,
                "description": "Toy uchun tayyor menyu",
                "is_available": True,
            },
        )

        Product.objects.get_or_create(
            business=royal,
            category=royal_cat,
            name="Premium Banket Set",
            defaults={
                "price": 180000,
                "description": "Kengaytirilgan toy menyusi",
                "is_available": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("🔥 Demo data yaratildi!"))
        self.stdout.write("Superadmin: admin / admin12345")
        self.stdout.write("Owner: owner1 / admin12345")
        self.stdout.write("Manager: manager1 / admin12345")