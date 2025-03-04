import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import load_data, save_data

# 記事分類
CATEGORIES = ["Memo", "Task", "Course"]

# 設定日誌記錄
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """啟動機器人時的歡迎訊息"""
    await update.message.reply_text("""您好，我是您的個人助理，：\n
        請使用：
        - /add <類別> <內容> 增加記事
        - /list 列出所有記事
        - /setreminder HH:MM 設定每日提醒時間
        - /schedule 啟動每日提醒
        """, parse_mode="Markdown")

async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """新增記事"""
    data = load_data()
    
    if len(context.args) < 2:
        await update.message.reply_text("格式錯誤，請使用 /add <類別> <內容>")
        return
    
    category, content = context.args[0], " ".join(context.args[1:])
    
    if category not in CATEGORIES:
        await update.message.reply_text(f"無效的類別！請選擇：{', '.join(CATEGORIES)}")
        return

    note = {"content": content, "category": category, "completed": False, "created_at": datetime.now().isoformat()}
    data["notes"].append(note)
    save_data(data)

    await update.message.reply_text(f"已新增記事：[ {category} ] {content}")

async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """列出所有未完成的記事"""
    data = load_data()
    notes = data["notes"]
    
    if not notes:
        await update.message.reply_text("目前沒有任何記事。")
        return

    message = "**未完成記事：**\n"
    keyboard = []

    for idx, note in enumerate(notes):
        if not note["completed"]:
            message += f"{idx + 1}. [{note['category']}] {note['content']}\n"
            keyboard.append([InlineKeyboardButton(f"完成 {idx + 1}", callback_data=f"done_{idx}")])

    if not keyboard:
        await update.message.reply_text("所有記事皆已完成！")
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup)

async def mark_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """標記記事為已完成"""
    query = update.callback_query
    await query.answer()
    
    data = load_data()
    note_index = int(query.data.split("_")[1])

    if 0 <= note_index < len(data["notes"]):
        data["notes"][note_index]["completed"] = True
        save_data(data)
        await query.edit_message_text("這則記事已標記為完成！")

async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """顯示目前設定的提醒時間"""
    data = load_data()
    reminder_time = data.get("reminder_time", "尚未設定")
    await update.message.reply_text(f"當前提醒時間：{reminder_time}")

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """設定每日提醒時間"""
    if not context.args:
        await update.message.reply_text("請提供時間（格式：HH:MM），例如 /setreminder 08:30")
        return

    try:
        time_str = context.args[0]
        datetime.strptime(time_str, "%H:%M")  # 確保格式正確
        data = load_data()
        data["reminder_time"] = time_str
        save_data(data)
        await update.message.reply_text(f"已設定每日提醒時間為 {time_str}")
    except ValueError:
        await update.message.reply_text("時間格式錯誤！請使用 HH:MM，例如 08:30")

async def schedule_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """在指定時間自動發送提醒"""
    data = load_data()
    reminder_time = data.get("reminder_time")
    
    if not reminder_time:
        await update.message.reply_text("請先設定提醒時間！\n使用 /setreminder HH:MM")
        return

    if context.job_queue is None:
        await update.message.reply_text("JobQueue is inactive.")
        return

    current_jobs = context.job_queue.get_jobs_by_name("daily_reminder")
    for job in current_jobs:
        job.schedule_removal()


    context.job_queue.run_daily(
            send_reminders,
            time=datetime.strptime(reminder_time, "%H:%M").time(),
            name="daily_reminder"
    )

    await update.message.reply_text(f"已設定每日提醒時間為 {reminder_time}")

async def send_reminders(context: ContextTypes.DEFAULT_TYPE) -> None:
    """發送未完成記事的提醒"""
    data = load_data()
    notes = [note for note in data["notes"] if not note["completed"]]

    if not notes:
        return

    message = "**每日提醒：**\n"
    for idx, note in enumerate(notes):
        message += f"{idx + 1}. [{note['category']}] {note['content']}\n"

    chat_id = data.get("chat_id")
    if not chat_id:
        logging.warning("無法發送提醒，chat_id 未設定")
        return

    try:
        await context.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logging.error(f"發送提醒失敗: {e}")
