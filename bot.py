import os
import random
import sqlite3
from io import BytesIO

from openpyxl import Workbook

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# =========================
# TOKEN (RAILWAY ENV)
# =========================
TOKEN = os.environ.get("TOKEN")

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("quiz.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    score INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0
)
""")
conn.commit()

# =========================
# QUESTIONS
# =========================
question_bank = {
    "easy": [
        {"q": "2 + 2 = ?", "o": ["4", "5", "6"], "a": "4"},
        {"q": "5 + 3 = ?", "o": ["8", "7", "6"], "a": "8"},
    ],
    "medium": [
        {"q": "12 × 2 = ?", "o": ["24", "20", "22"], "a": "24"},
        {"q": "18 ÷ 2 = ?", "o": ["9", "8", "7"], "a": "9"},
    ],
    "hard": [
        {"q": "√81 = ?", "o": ["9", "8", "7"], "a": "9"},
        {"q": "15² = ?", "o": ["225", "200", "210"], "a": "225"},
    ]
}

# =========================
# USER STATE
# =========================
user_state = {}

# =========================
# DB FUNCTIONS
# =========================
def add_user(user_id, username):
    cursor.execute("""
    INSERT OR IGNORE INTO users VALUES (?, ?, 0, 0, 0)
    """, (user_id, username))
    conn.commit()

def update_score(user_id, correct):
    if correct:
        cursor.execute("""
        UPDATE users
        SET score = score + 1,
            correct_answers = correct_answers + 1
        WHERE user_id = ?
        """, (user_id,))
    else:
        cursor.execute("""
        UPDATE users
        SET wrong_answers = wrong_answers + 1
        WHERE user_id = ?
        """, (user_id,))
    conn.commit()

def get_top():
    cursor.execute("""
    SELECT username, score
    FROM users
    ORDER BY score DESC
    LIMIT 10
    """)
    return cursor.fetchall()

def get_user_stats(user_id):
    cursor.execute("""
    SELECT score, correct_answers, wrong_answers
    FROM users
    WHERE user_id = ?
    """, (user_id,))
    return cursor.fetchone()

# =========================
# EXCEL EXPORT (RAILWAY SAFE)
# =========================
def export_excel():
    cursor.execute("""
    SELECT username, score, correct_answers, wrong_answers
    FROM users
    """)

    rows = cursor.fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    ws.append(["Username", "Score", "Correct", "Wrong"])

    for r in rows:
        ws.append(r)

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return file_stream

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    add_user(user.id, user.username)

    keyboard = [
        [InlineKeyboardButton("Легкий", callback_data="easy")],
        [InlineKeyboardButton("Средний", callback_data="medium")],
        [InlineKeyboardButton("Сложный", callback_data="hard")]
    ]

    await update.message.reply_text(
        "🎮 Выбери сложность:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# BUTTON HANDLER
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # выбор сложности
    if data in question_bank:
        pool = random.sample(question_bank[data], len(question_bank[data]))

        user_state[user_id] = {
            "level": data,
            "pool": pool,
            "index": 0
        }

        await send_question(query.message, user_id)
        return

    # ответ
    if user_id in user_state:
        state = user_state[user_id]
        q = state["pool"][state["index"]]

        if data == q["a"]:
            update_score(user_id, True)
            await query.message.reply_text("✅ Верно!")
        else:
            update_score(user_id, False)
            await query.message.reply_text(f"❌ Неверно! Ответ: {q['a']}")

        state["index"] += 1
        await send_question(query.message, user_id)

# =========================
# QUESTION SENDER
# =========================
async def send_question(message, user_id):

    state = user_state[user_id]
    pool = state["pool"]
    i = state["index"]

    # конец теста
    if i >= len(pool):

        stats = get_user_stats(user_id)

        if stats:
            score, c, w = stats
            percent = round((c / (c + w)) * 100, 2) if (c + w) > 0 else 0

            await message.reply_text(
                "🏁 ТЕСТ ЗАВЕРШЕН\n\n"
                f"🏆 Баллы: {score}\n"
                f"✅ Правильных: {c}\n"
                f"❌ Ошибок: {w}\n"
                f"📊 Процент: {percent}%"
            )
        return

    q = pool[i]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=opt)]
        for opt in q["o"]
    ]

    await message.reply_text(
        f"❓ {q['q']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# TOP
# =========================
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = get_top()

    text = "🏆 ТОП игроков:\n\n"

    for i, r in enumerate(rows, 1):
        text += f"{i}. {r[0]} — {r[1]}\n"

    await update.message.reply_text(text)

# =========================
# RESTART
# =========================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id in user_state:
        user_state[user_id]["index"] = 0

    await update.message.reply_text("🔄 Тест перезапущен!")
    await send_question(update.message, user_id)

# =========================
# EXPORT EXCEL
# =========================
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):

    file_stream = export_excel()

    await update.message.reply_document(
        document=file_stream,
        filename="results.xlsx"
    )

# =========================
# MAIN
# =========================
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
