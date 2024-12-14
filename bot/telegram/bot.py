from django.conf import settings
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.telegram.handlers import start_handler, start_location, hint_handler, show_balance, \
    finish_location, process_answer

application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start_handler))
application.add_handler(CallbackQueryHandler(start_location, pattern=r"^start_location_\d+$"))
application.add_handler(CallbackQueryHandler(hint_handler, pattern=r"^hint_\d+$"))
application.add_handler(CallbackQueryHandler(show_balance, pattern=r"^show_balance$"))
application.add_handler(CallbackQueryHandler(finish_location, pattern=r"^finish_location_\d+$"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_answer))
application.add_handler(CallbackQueryHandler(hint_handler, pattern=r"^hint_\d+(_\d+)?$"))

application.run_polling()
