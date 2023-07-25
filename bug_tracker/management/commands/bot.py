from django.core.management.base import BaseCommand
from django.conf import settings
from telebot import TeleBot
from bug_tracker.models import TelegramUser

bot = TeleBot(settings.TELEGRAM_BOT_API_KEY, threaded=False)


class Command(BaseCommand):
    help = "Implemented to Django application telegram bot setup command"

    def handle(self, *args, **kwargs):
        @bot.message_handler(func=lambda message: True)
        def handle_message(message):
            chat_id = message.chat.id
            token = message.text

            try:
                telegram_user = TelegramUser.objects.get(token=token)
                telegram_user.chat_id = chat_id
                telegram_user.save()
                bot.reply_to(message,
                             "Chat ID has been associated with your token.")
            except TelegramUser.DoesNotExist:
                bot.reply_to(message, "Invalid token. Please try again.")

        bot.infinity_polling()
