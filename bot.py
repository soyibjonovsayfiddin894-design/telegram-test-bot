import asyncio
import sqlite3
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "7950544353:AAHUqnGPJaizx2KAa-dOIiusxEd1GqwVbnc"

# ================= DATABASE =================

conn = sqlite3.connect("quiz.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER,
    question TEXT,
    a TEXT,
    b TEXT,
    c TEXT,
    d TEXT,
    correct TEXT
)
""")

conn.commit()

# ================= USER STATE =================

user_data_temp = {}
active_tests = {}

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Test yaratish", callback_data="create_test")],
        [InlineKeyboardButton("▶ Test boshlash", callback_data="start_test")]
    ]
    await update.message.reply_text(
        "Quiz Botga xush kelibsiz!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= CREATE TEST =================

async def create_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Test nomini yozing:")
    context.user_data["creating_test"] = True


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # ===== Test yaratish boshlanishi =====
    if context.user_data.get("creating_test"):
        cursor.execute("INSERT INTO quizzes (name) VALUES (?)", (text,))
        conn.commit()
        quiz_id = cursor.lastrowid
        user_data_temp[user_id] = {"quiz_id": quiz_id}
        context.user_data["creating_test"] = False
        context.user_data["adding_question"] = True
        await update.message.reply_text("Savol yozing:")
        return

    # ===== Savol qo'shish =====
    if context.user_data.get("adding_question"):
        user_data_temp[user_id]["question"] = text
        context.user_data["adding_question"] = False
        context.user_data["adding_options"] = True
        await update.message.reply_text("4 ta javobni vergul bilan yozing:\nMasalan: A,B,C,D")
        return

    # ===== Variantlar =====
    if context.user_data.get("adding_options"):
        parts = text.split(",")
        if len(parts) != 4:
            await update.message.reply_text("Iltimos 4 ta variant kiriting.")
            return

        user_data_temp[user_id]["a"] = parts[0].strip()
        user_data_temp[user_id]["b"] = parts[1].strip()
        user_data_temp[user_id]["c"] = parts[2].strip()
        user_data_temp[user_id]["d"] = parts[3].strip()

        keyboard = [
            [
                InlineKeyboardButton("A", callback_data="correct_A"),
                InlineKeyboardButton("B", callback_data="correct_B"),
                InlineKeyboardButton("C", callback_data="correct_C"),
                InlineKeyboardButton("D", callback_data="correct_D"),
            ]
        ]

        context.user_data["adding_options"] = False
        await update.message.reply_text(
            "To‘g‘ri javobni tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ===== Test nomi yozib boshlash =====
    cursor.execute("SELECT id FROM quizzes WHERE name=?", (text,))
    quiz = cursor.fetchone()
    if quiz:
        quiz_id = quiz[0]
        keyboard = []
        for sec in range(30, 121, 15):
            keyboard.append([InlineKeyboardButton(f"{sec} sek", callback_data=f"time_{quiz_id}_{sec}")])
        await update.message.reply_text(
            "Savollar oralig'ini tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ================= TO‘G‘RI JAVOB =================
async def correct_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    correct = query.data.split("_")[1]

    data = user_data_temp[user_id]

    cursor.execute("""
    INSERT INTO questions (quiz_id, question, a, b, c, d, correct)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["quiz_id"],
        data["question"],
        data["a"],
        data["b"],
        data["c"],
        data["d"],
        correct
    ))

    conn.commit()

    context.user_data["adding_question"] = True
    await query.message.reply_text("Savol saqlandi.\nYana savol yozing yoki /start bosing.")


# ================= TEST BOSHLASH =================

async def time_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, quiz_id, sec = query.data.split("_")
    quiz_id = int(quiz_id)
    sec = int(sec)

    cursor.execute("SELECT * FROM questions WHERE quiz_id=?", (quiz_id,))
    questions = cursor.fetchall()

    if not questions:
        await query.message.reply_text("Bu testda savol yo‘q.")
        return

    active_tests[query.from_user.id] = {
        "questions": questions,
        "index": 0,
        "score": 0,
        "timeout_count": 0,
        "interval": sec
    }

    await send_question(query.from_user.id, query.message, context)


async def send_question(user_id, message, context):
    test = active_tests[user_id]

    if test["index"] >= len(test["questions"]):
        await message.reply_text(f"Test tugadi.\nNatija: {test['score']} / {len(test['questions'])}")
        active_tests.pop(user_id)
        return

    q = test["questions"][test["index"]]

    keyboard = [
        [
            InlineKeyboardButton(q[3], callback_data=f"ans_A"),
            InlineKeyboardButton(q[4], callback_data=f"ans_B"),
        ],
        [
            InlineKeyboardButton(q[5], callback_data=f"ans_C"),
            InlineKeyboardButton(q[6], callback_data=f"ans_D"),
        ]
    ]

    await message.reply_text(
        f"{q[2]}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.job_queue.run_once(
        timeout_handler,
        test["interval"],
        data=user_id
    )


async def timeout_handler(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data
    if user_id not in active_tests:
        return

    test = active_tests[user_id]
    test["timeout_count"] += 1

    if test["timeout_count"] >= 3:
        await context.bot.send_message(user_id, "3 ta savol javobsiz qoldi. Test to‘xtatildi.")
        active_tests.pop(user_id)
        return

    test["index"] += 1
    await send_question(user_id, await context.bot.get_chat(user_id), context)


async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in active_tests:
        return

    test = active_tests[user_id]
    q = test["questions"][test["index"]]
    correct = q[7]

    chosen = query.data.split("_")[1]

    if chosen == correct:
        test["score"] += 1

    test["index"] += 1
    await send_question(user_id, query.message, context)


# ================= MAIN =================

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(create_test, pattern="create_test"))
    app.add_handler(CallbackQueryHandler(correct_answer, pattern="correct_"))
    app.add_handler(CallbackQueryHandler(time_selected, pattern="time_"))
    app.add_handler(CallbackQueryHandler(answer_handler, pattern="ans_"))

    app.run_polling()

if __name__ == "__main__":
    main()