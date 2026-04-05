import os
from datetime import datetime
from pathlib import Path

import telebot
from telebot import types

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from dotenv import load_dotenv
from config.settings import BASE_DIR
from coreapp.models import (
    Customer,
    Business,
    BusinessStaff,
    Branch,
    Place,
    Booking,
    Product,
)

load_dotenv(BASE_DIR / ".env")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Foydalanuvchi step ma'lumotlari shu dict ichida saqlanadi.
user_data = {}


@bot.message_handler(commands=["start"])
def start_handler(message):
    customer, _ = Customer.objects.get_or_create(
        telegram_id=message.from_user.id,
        defaults={
            "full_name": message.from_user.full_name or "User",
            "username": message.from_user.username or "",
        }
    )

    customer.full_name = message.from_user.full_name or "User"
    customer.username = message.from_user.username or ""
    customer.save()

    # telefon yo'q bo'lsa so'raymiz
    if not customer.phone:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton("📱 Telefon yuborish", request_contact=True))

        user_data[message.chat.id] = {"step": "get_phone"}

        bot.send_message(
            message.chat.id,
            "📱 Iltimos telefon raqamingizni yuboring:",
            reply_markup=kb
        )
        return

    bot.send_message(
        message.chat.id,
        "Assalomu alaykum. Booking botga xush kelibsiz.",
        reply_markup=main_menu()
    )
@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    if user_data.get(message.chat.id, {}).get("step") != "get_phone":
        return

    phone = message.contact.phone_number

    customer, _ = Customer.objects.get_or_create(
        telegram_id=message.from_user.id,
        defaults={
            "full_name": message.from_user.full_name or "User",
            "username": message.from_user.username or "",
        }
    )

    customer.full_name = message.from_user.full_name or "User"
    customer.username = message.from_user.username or ""
    customer.phone = phone
    customer.save()

    user_data.pop(message.chat.id, None)

    bot.send_message(
        message.chat.id,
        "✅ Telefon saqlandi! Endi foydalanishingiz mumkin.",
        reply_markup=main_menu()
    )
    if user_data.get(message.chat.id, {}).get("step") != "get_phone":
        return

    phone = message.contact.phone_number

    customer = Customer.objects.get(telegram_id=message.from_user.id)
    customer.phone = phone
    customer.save()

    bot.send_message(
        message.chat.id,
        "✅ Telefon saqlandi! Endi foydalanishingiz mumkin.",
        reply_markup=main_menu()
    )

    user_data.pop(message.chat.id, None)
def reset_user(chat_id):
    user_data.pop(chat_id, None)


def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🏢 Bizneslar", "📅 Mening bronlarim")
    kb.row("❌ Bronni bekor qilish", "👑 Owner bronlarim")
    kb.row("🧹 Bekor qilish")
    return kb


def cancel_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🧹 Bekor qilish")
    return kb


def owner_keyboard(booking_id):
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("✅ Confirm", callback_data=f"owner_confirm:{booking_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"owner_reject:{booking_id}")
    )
    return kb


def cancel_booking_keyboard(rows):
    kb = types.InlineKeyboardMarkup()
    for row in rows:
        if row.status in ["pending", "confirmed"]:
            kb.add(
                types.InlineKeyboardButton(
                    f"{row.booking_code} | {row.business.name} | {row.booking_date}",
                    callback_data=f"client_cancel:{row.id}"
                )
            )
    return kb


def get_or_create_customer(message):
    customer, _ = Customer.objects.get_or_create(
        telegram_id=message.from_user.id,
        defaults={
            "full_name": message.from_user.full_name or "User",
            "username": message.from_user.username or "",
        },
    )
    customer.full_name = message.from_user.full_name or "User"
    customer.username = message.from_user.username or ""
    customer.save()
    return customer


def booking_code():
    return "BRON-" + datetime.now().strftime("%Y%m%d%H%M%S%f")


def validate_date(text):
    try:
        d = datetime.strptime(text, "%Y-%m-%d").date()
        return d >= datetime.now().date()
    except Exception:
        return False


def validate_time(text):
    try:
        datetime.strptime(text, "%H:%M")
        return True
    except Exception:
        return False




@bot.message_handler(func=lambda m: m.text == "🏢 Bizneslar")
def businesses_handler(message):
    rows = Business.objects.filter(is_active=True).order_by("id")
    if not rows:
        bot.send_message(message.chat.id, "Bizneslar topilmadi.")
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in rows:
        kb.add(f"BUSINESS_{row.id} | {row.name}")
    kb.add("🧹 Bekor qilish")

    user_data[message.chat.id] = {"step": "choose_business"}
    bot.send_message(message.chat.id, "Biznes tanlang:", reply_markup=kb)


@bot.message_handler(func=lambda m: m.text == "📅 Mening bronlarim")
def my_bookings_handler(message):
    rows = Booking.objects.filter(
        customer__telegram_id=message.from_user.id
    ).select_related("business", "branch", "place", "customer").order_by("-id")

    if not rows:
        bot.send_message(message.chat.id, "Sizda hali bronlar yo'q.", reply_markup=main_menu())
        return

    text = "📅 Mening bronlarim:\n\n"
    for row in rows:
        text += (
            f"ID: {row.id}\n"
            f"Kod: {row.booking_code}\n"
            f"Biznes: {row.business.name}\n"
            f"Filial: {row.branch.name}\n"
            f"Joy: {row.place.name}\n"
            f"Sana: {row.booking_date}\n"
            f"Vaqt: {row.start_time} - {row.end_time}\n"
            f"Status: {row.status}\n\n"
        )

    bot.send_message(message.chat.id, text, reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text == "👑 Owner bronlarim")
def owner_bookings_handler(message):
    rows = Booking.objects.filter(
        business__staff_members__telegram_id=message.from_user.id,
        business__staff_members__is_active=True
    ).select_related("customer", "business", "branch", "place").distinct().order_by("-id")

    if not rows:
        bot.send_message(message.chat.id, "Sizga tegishli owner bronlar topilmadi.", reply_markup=main_menu())
        return

    text = "👑 Owner bronlarim:\n\n"
    for row in rows[:10]:
        text += (
            f"ID: {row.id}\n"
            f"Kod: {row.booking_code}\n"
            f"Mijoz: {row.customer.full_name}\n"
            f"Biznes: {row.business.name}\n"
            f"Sana: {row.booking_date}\n"
            f"Status: {row.status}\n\n"
        )

    bot.send_message(message.chat.id, text, reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text == "❌ Bronni bekor qilish")
def cancel_menu_handler(message):
    rows = Booking.objects.filter(
        customer__telegram_id=message.from_user.id,
        status__in=["pending", "confirmed"]
    ).select_related("business").order_by("-id")

    if not rows:
        bot.send_message(message.chat.id, "Bekor qilinadigan bronlar yo'q.", reply_markup=main_menu())
        return

    bot.send_message(
        message.chat.id,
        "Bekor qilinadigan bookingni tanlang:",
        reply_markup=cancel_booking_keyboard(rows)
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("client_cancel:"))
def client_cancel_callback(call):
    booking_id = int(call.data.split(":")[1])

    try:
        booking = Booking.objects.select_related("business", "customer").get(id=booking_id)
    except Booking.DoesNotExist:
        bot.answer_callback_query(call.id, "Booking topilmadi")
        return

    if booking.customer.telegram_id != call.from_user.id:
        bot.answer_callback_query(call.id, "Bu sizning booking emas")
        return

    booking.status = "cancelled"
    booking.save()

    bot.answer_callback_query(call.id, "Booking bekor qilindi")
    bot.send_message(
        call.message.chat.id,
        f"❌ Booking bekor qilindi: {booking.booking_code}",
        reply_markup=main_menu()
    )

    for staff in BusinessStaff.objects.filter(
        business=booking.business,
        is_active=True
    ).exclude(telegram_id__isnull=True):
        try:
            bot.send_message(
                staff.telegram_id,
                f"⚠️ Mijoz bookingni bekor qildi. Kod: {booking.booking_code}"
            )
        except Exception:
            pass


@bot.message_handler(func=lambda m: m.text == "🧹 Bekor qilish")
def cancel_handler(message):
    reset_user(message.chat.id)
    bot.send_message(message.chat.id, "Jarayon bekor qilindi.", reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text.startswith("BUSINESS_"))
def business_selected_handler(message):
    try:
        business_id = int(message.text.split("|")[0].replace("BUSINESS_", "").strip())
        business = Business.objects.get(id=business_id, is_active=True)
    except Exception:
        bot.send_message(message.chat.id, "Biznesni tanlashda xato bo'ldi.")
        return

    user_data.setdefault(message.chat.id, {})
    user_data[message.chat.id]["business"] = business.id
    user_data[message.chat.id]["step"] = "business_action"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📍 Filiallar", "🍽 Menu")
    kb.row("🧹 Bekor qilish")

    bot.send_message(
        message.chat.id,
        f"<b>{business.name}</b>\nKerakli bo'limni tanlang:",
        reply_markup=kb
    )


@bot.message_handler(func=lambda m: m.text == "📍 Filiallar")
def show_branches_handler(message):
    data = user_data.get(message.chat.id, {})
    business_id = data.get("business")

    if not business_id:
        bot.send_message(message.chat.id, "Avval biznes tanlang.", reply_markup=main_menu())
        return

    rows = Branch.objects.filter(business_id=business_id, is_active=True).order_by("id")
    if not rows:
        bot.send_message(message.chat.id, "Bu biznes uchun filiallar topilmadi.", reply_markup=main_menu())
        return

    user_data[message.chat.id]["step"] = "choose_branch"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in rows:
        kb.add(f"BRANCH_{row.id} | {row.name}")
    kb.add("🧹 Bekor qilish")

    bot.send_message(message.chat.id, "Filial tanlang:", reply_markup=kb)


@bot.message_handler(func=lambda m: m.text == "🍽 Menu")
def show_menu_handler(message):
    data = user_data.get(message.chat.id, {})
    business_id = data.get("business")

    if not business_id:
        bot.send_message(message.chat.id, "Avval biznes tanlang.", reply_markup=main_menu())
        return

    products = Product.objects.filter(
        business_id=business_id,
        is_available=True
    ).select_related("category").order_by("category__name", "name")

    if not products:
        bot.send_message(message.chat.id, "Bu restoran uchun menu topilmadi.")
        return

    text = "🍽 <b>Menu</b>\n\n"

    current_category = None
    for product in products:
        category_name = product.category.name if product.category else "Boshqa"

        if current_category != category_name:
            current_category = category_name
            text += f"\n<b>{current_category}</b>\n"

        text += f"• {product.name} — {int(product.price)} so'm\n"
        if product.description:
            text += f"  {product.description}\n"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📍 Filiallar")
    kb.row("🧹 Bekor qilish")

    bot.send_message(message.chat.id, text, reply_markup=kb)


@bot.message_handler(func=lambda m: m.text.startswith("BRANCH_"))
def branch_selected_handler(message):
    try:
        branch_id = int(message.text.split("|")[0].replace("BRANCH_", "").strip())
        branch = Branch.objects.select_related("business").get(id=branch_id, is_active=True)
    except Exception:
        bot.send_message(message.chat.id, "Filialni tanlashda xato bo'ldi.")
        return

    user_data.setdefault(message.chat.id, {})
    user_data[message.chat.id]["branch"] = branch.id
    user_data[message.chat.id]["step"] = "enter_date"

    bot.send_message(
        message.chat.id,
        "Sana kiriting.\nFormat: YYYY-MM-DD\nMasalan: 2026-04-10",
        reply_markup=cancel_menu()
    )


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "enter_date")
def date_handler(message):
    text = message.text.strip()

    if not validate_date(text):
        bot.send_message(message.chat.id, "Sana noto'g'ri yoki o'tgan kun.\nMasalan: 2026-04-10")
        return

    user_data[message.chat.id]["booking_date"] = text
    user_data[message.chat.id]["step"] = "enter_start_time"

    bot.send_message(
        message.chat.id,
        "Boshlanish vaqtini kiriting.\nFormat: HH:MM\nMasalan: 18:00",
        reply_markup=cancel_menu()
    )


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "enter_start_time")
def start_time_handler(message):
    text = message.text.strip()

    if not validate_time(text):
        bot.send_message(message.chat.id, "Vaqt noto'g'ri. Masalan: 18:00")
        return

    user_data[message.chat.id]["start_time"] = text
    user_data[message.chat.id]["step"] = "enter_end_time"

    bot.send_message(
        message.chat.id,
        "Tugash vaqtini kiriting.\nFormat: HH:MM\nMasalan: 20:00",
        reply_markup=cancel_menu()
    )


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "enter_end_time")
def end_time_handler(message):
    text = message.text.strip()

    if not validate_time(text):
        bot.send_message(message.chat.id, "Vaqt noto'g'ri. Masalan: 20:00")
        return

    start_time = user_data[message.chat.id]["start_time"]

    try:
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(text, "%H:%M")
        if end_dt <= start_dt:
            bot.send_message(message.chat.id, "Tugash vaqti boshlanishdan katta bo'lishi kerak.")
            return
    except Exception:
        bot.send_message(message.chat.id, "Vaqt formatida xato.")
        return

    user_data[message.chat.id]["end_time"] = text

    branch_id = user_data[message.chat.id]["branch"]
    booking_date = user_data[message.chat.id]["booking_date"]

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        bot.send_message(message.chat.id, "Filial topilmadi.", reply_markup=main_menu())
        reset_user(message.chat.id)
        return

    all_places = Place.objects.filter(branch=branch, is_active=True).order_by("id")
    available_places = []

    start_time_obj = datetime.strptime(user_data[message.chat.id]["start_time"], "%H:%M").time()
    end_time_obj = datetime.strptime(user_data[message.chat.id]["end_time"], "%H:%M").time()

    for place in all_places:
        conflicts = Booking.objects.filter(
            place=place,
            booking_date=booking_date,
            status__in=["pending", "confirmed"]
        )

        is_busy = False
        for booking in conflicts:
            if start_time_obj < booking.end_time and booking.start_time < end_time_obj:
                is_busy = True
                break

        if not is_busy:
            available_places.append(place)

    if not available_places:
        bot.send_message(
            message.chat.id,
            "Bu sana va vaqt uchun bo'sh joy topilmadi. Boshqa vaqt tanlang.",
            reply_markup=main_menu()
        )
        reset_user(message.chat.id)
        return

    user_data[message.chat.id]["step"] = "choose_place"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in available_places:
        kb.add(f"PLACE_{row.id} | {row.name} | {row.capacity} kishi")
    kb.add("🧹 Bekor qilish")

    bot.send_message(message.chat.id, "Bo'sh joy tanlang:", reply_markup=kb)


@bot.message_handler(func=lambda m: m.text.startswith("PLACE_"))
def place_selected_handler(message):
    try:
        place_id = int(message.text.split("|")[0].replace("PLACE_", "").strip())
        Place.objects.select_related("branch", "branch__business").get(id=place_id, is_active=True)
    except Exception:
        bot.send_message(message.chat.id, "Joyni tanlashda xato bo'ldi.")
        return

    user_data.setdefault(message.chat.id, {})
    user_data[message.chat.id]["place"] = place_id
    user_data[message.chat.id]["step"] = "enter_guests"

    bot.send_message(
        message.chat.id,
        "Odam sonini kiriting.\nMasalan: 4",
        reply_markup=cancel_menu()
    )


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "enter_guests")
def guests_handler(message):
    text = message.text.strip()

    if not text.isdigit():
        bot.send_message(message.chat.id, "Faqat raqam kiriting. Masalan: 4")
        return

    guests = int(text)
    if guests <= 0:
        bot.send_message(message.chat.id, "Odam soni 1 dan katta bo'lishi kerak.")
        return

    user_data[message.chat.id]["guests_count"] = guests
    user_data[message.chat.id]["step"] = "enter_note"

    bot.send_message(
        message.chat.id,
        "Izoh kiriting yoki `-` yuboring.",
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    )


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "enter_note")
def note_handler(message):
    note = message.text.strip()
    if note == "-":
        note = ""

    user_data[message.chat.id]["note"] = note
    user_data[message.chat.id]["step"] = "confirm"

    data = user_data[message.chat.id]
    text = (
        "📌 Bron ma'lumoti:\n\n"
        f"Biznes ID: {data['business']}\n"
        f"Filial ID: {data['branch']}\n"
        f"Joy ID: {data['place']}\n"
        f"Sana: {data['booking_date']}\n"
        f"Boshlanish: {data['start_time']}\n"
        f"Tugash: {data['end_time']}\n"
        f"Odam soni: {data['guests_count']}\n"
        f"Izoh: {data['note'] or '-'}\n\n"
        "Tasdiqlaysizmi?"
    )

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("✅ Tasdiqlash", "🧹 Bekor qilish")
    bot.send_message(message.chat.id, text, reply_markup=kb)


@bot.message_handler(func=lambda m: m.text == "✅ Tasdiqlash")
def confirm_handler(message):
    data = user_data.get(message.chat.id)
    if not data:
        bot.send_message(message.chat.id, "Ma'lumot topilmadi. Qaytadan boshlang.", reply_markup=main_menu())
        return

    customer = get_or_create_customer(message)

    try:
        business = Business.objects.get(id=data["business"], is_active=True)
        branch = Branch.objects.get(id=data["branch"], is_active=True)
        place = Place.objects.get(id=data["place"], is_active=True)
    except Exception:
        bot.send_message(message.chat.id, "Business/branch/place topilmadi.", reply_markup=main_menu())
        reset_user(message.chat.id)
        return

    booking = Booking(
        booking_code=booking_code(),
        customer=customer,
        business=business,
        branch=branch,
        place=place,
        booking_date=data["booking_date"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        guests_count=data["guests_count"],
        note=data["note"],
        status="pending",
    )

    try:
        booking.save()
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Booking yaratilmadi: {e}", reply_markup=main_menu())
        reset_user(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        f"✅ Bron muvaffaqiyatli yaratildi.\n\nKod: {booking.booking_code}\nStatus: {booking.status}",
        reply_markup=main_menu()
    )

    staff_rows = BusinessStaff.objects.filter(
        business=business,
        is_active=True
    ).exclude(telegram_id__isnull=True)

    owner_text = (
    "🔥 <b>YANGI BRON!</b>\n\n"
    f"👤 Mijoz: {customer.full_name}\n"
    f"🏢 Biznes: {business.name}\n"
    f"📍 Filial: {branch.name}\n"
    f"🪑 Joy: {place.name}\n"
    f"📅 Sana: {booking.booking_date}\n"
    f"⏰ Vaqt: {booking.start_time} - {booking.end_time}\n"
    f"👥 Odam: {booking.guests_count}\n"
    f"📝 Izoh: {booking.note or '-'}"
    )

    for staff in staff_rows:
        try:
            bot.send_message(
                staff.telegram_id,
                owner_text,
                reply_markup=owner_keyboard(booking.id)
            )
        except Exception:
            pass

    reset_user(message.chat.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("owner_confirm:"))
def owner_confirm_callback(call):
    booking_id = int(call.data.split(":")[1])

    try:
        booking = Booking.objects.select_related("business", "customer").get(id=booking_id)
    except Booking.DoesNotExist:
        bot.answer_callback_query(call.id, "Booking topilmadi")
        return

    allowed = BusinessStaff.objects.filter(
        business=booking.business,
        telegram_id=call.from_user.id,
        is_active=True
    ).exists()

    if not allowed:
        bot.answer_callback_query(call.id, "Bu sizning booking emas")
        return

    booking.status = "confirmed"
    booking.save()

    bot.answer_callback_query(call.id, "Confirmed")
    bot.send_message(call.message.chat.id, f"✅ Booking tasdiqlandi: {booking.booking_code}")

    try:
        bot.send_message(
            booking.customer.telegram_id,
            f"✅ Booking tasdiqlandi. Kod: {booking.booking_code}"
        )
    except Exception:
        pass


@bot.callback_query_handler(func=lambda c: c.data.startswith("owner_reject:"))
def owner_reject_callback(call):
    booking_id = int(call.data.split(":")[1])

    try:
        booking = Booking.objects.select_related("business", "customer").get(id=booking_id)
    except Booking.DoesNotExist:
        bot.answer_callback_query(call.id, "Booking topilmadi")
        return

    allowed = BusinessStaff.objects.filter(
        business=booking.business,
        telegram_id=call.from_user.id,
        is_active=True
    ).exists()

    if not allowed:
        bot.answer_callback_query(call.id, "Bu sizning booking emas")
        return

    booking.status = "rejected"
    booking.save()

    bot.answer_callback_query(call.id, "Rejected")
    bot.send_message(call.message.chat.id, f"❌ Booking rad etildi: {booking.booking_code}")

    try:
        bot.send_message(
            booking.customer.telegram_id,
            f"❌ Booking rad etildi. Kod: {booking.booking_code}"
        )
    except Exception:
        pass


if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling()