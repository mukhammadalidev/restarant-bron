# Expanded Booking System

Telegram bot + web panel + ko'p restoran adminlari uchun kengaytirilgan loyiha.

## Nimalar ishlaydi
- Telegram bot orqali bron qilish
- Ko'p biznes / ko'p filial / ko'p joy
- Har bir biznesga bir nechta admin biriktirish
- Booking yaratilganda shu biznes adminlariga Telegram xabar ketadi
- Admin botdan Confirm / Reject qila oladi
- Mijozga status haqida xabar qaytadi
- Mijoz o'z bookinglarini ko'radi
- Mijoz bookingni bekor qila oladi
- Web panel:
  - login
  - dashboard
  - branch list/create/edit
  - place list/create/edit
  - booking list
- Django admin:
  - barcha bizneslar
  - staff/adminlar
  - telegram id lar
  - bookinglar

## O'rnatish
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
```

## Ishga tushirish
```bash
python manage.py runserver
```

Yangi terminal:
```bash
source venv/bin/activate
python bot.py
```

## Demo loginlar
- superadmin: `admin / admin12345`
- restoran admin: `owner1 / admin12345`
- restoran manager: `manager1 / admin12345`

## Muhim
Siz faqat `.env` ichiga `BOT_TOKEN` yozasiz.

Ownerga xabar borishi uchun owner ham botga 1 marta `/start` bosishi kerak.
