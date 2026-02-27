from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes
)
from database import Database
from keyboards import main_keyboard, part_keyboard, yes_no_keyboard
import random
import os

TOKEN = os.getenv("BOT_TOKEN")  # yoki to‘g‘ridan-to‘g‘ri yozish: "8665947409:AA...etc"
CHANNEL_ID = "@kakgovorytmujik"

db = Database("ielts.db")

# Start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    if db.get_user(user.id) is None:
        await update.message.reply_text("Salom! Ismingizni yozing:")
        return
    await update.message.reply_text(
        f"Salom, {user.first_name}! Testni boshlash uchun menyudan tanlang:",
        reply_markup=main_keyboard()
    )

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = update.message.text
    db.add_user(user.id, name)
    await update.message.reply_text(
        f"Rahmat, {name}! Testni boshlash uchun menyudan tanlang:",
        reply_markup=main_keyboard()
    )

# Kanalga obuna tekshirish
async def check_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
    return member.status != "left"

# Part1/Part2 handler
async def part_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    part = query.data
    questions = db.get_random_questions(part, 5)
    context.user_data["questions"] = questions
    context.user_data["index"] = 0
    await send_question(query.message, context)

async def send_question(message, context):
    index = context.user_data["index"]
    questions = context.user_data["questions"]
    if index >= len(questions):
        await message.reply_text(
            "Savollar tugadi. Yana test qilmoqchimisiz?",
            reply_markup=yes_no_keyboard()
        )
        return
    q = questions[index]
    text = f"{q['question']}\nA. {q['a']}\nB. {q['b']}\nC. {q['c']}\nD. {q['d']}"
    await message.reply_text(text)
    context.user_data["index"] += 1

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "yes":
        # yangi random 5 savol
        part = context.user_data.get("current_part", "part1")
        questions = db.get_random_questions(part, 5)
        context.user_data["questions"] = questions
        context.user_data["index"] = 0
        await send_question(query.message, context)
    else:
        await query.message.reply_text("Test tugadi. Keyinroq yana urinib ko‘ring.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlerlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(part_handler, pattern="^part"))
    app.add_handler(CallbackQueryHandler(next_question, pattern="^(yes|no)$"))
    app.add_handler(CommandHandler("name", set_name))

    app.run_polling()

if __name__ == "__main__":
    main()
