import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, JobQueue

from handlers import start, add_note, list_notes, reminder, set_reminder, schedule_reminders, mark_done
from utils import load_data

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Cannot find TOKEN, please check your .env file.")

load_data()

def main():
    """這裡不使用 async，直接讓 `app.run_polling()` 管理事件迴圈"""
    app = Application.builder().token(TOKEN).build()

    if app.job_queue is None:
        raise RuntimeError(
                """JobQueue cannot initialize,
                 please check python-telegram-bot[job_queue] be installed correctly.
                """)

    app.job_queue.start()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_note))
    app.add_handler(CommandHandler("list", list_notes))
    app.add_handler(CommandHandler("reminder", reminder))
    app.add_handler(CommandHandler("setreminder", set_reminder))
    app.add_handler(CommandHandler("schedule", schedule_reminders))
    app.add_handler(CallbackQueryHandler(mark_done, pattern="^done_\\d+$"))

    logging.info("Starting bot...")
    app.run_polling()  # 讓 `Application` 自己管理事件迴圈

if __name__ == "__main__":
    main()  # 直接呼叫 `main()`，不使用 asyncio.run()

