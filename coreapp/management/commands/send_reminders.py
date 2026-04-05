from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from coreapp.models import Booking
import telebot
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


class Command(BaseCommand):
    help = "1 soat oldin reminder yuboradi"

    def handle(self, *args, **kwargs):
        now = datetime.now()

        # 1 soatdan keyingi vaqt
        reminder_time = now + timedelta(hours=1)

        bookings = Booking.objects.filter(
            booking_date=reminder_time.date(),
            status="confirmed"
        )

        count = 0

        for booking in bookings:
            start_datetime = datetime.combine(
                booking.booking_date,
                booking.start_time
            )

            # agar 55-65 minut oralig‘ida bo‘lsa
            diff = (start_datetime - now).total_seconds() / 60

            if 55 <= diff <= 65:
                try:
                    bot.send_message(
                        booking.customer.telegram_id,
                        f"⏰ Eslatma!\n\n"
                        f"1 soatdan keyin booking boshlanadi!\n\n"
                        f"📅 Sana: {booking.booking_date}\n"
                        f"⏰ Vaqt: {booking.start_time} - {booking.end_time}\n"
                        f"🏢 {booking.business.name}\n"
                        f"📍 {booking.branch.name}\n"
                        f"🪑 {booking.place.name}"
                    )
                    count += 1
                except Exception as e:
                    print("ERROR:", e)

        self.stdout.write(self.style.SUCCESS(f"Yuborildi: {count} ta reminder"))