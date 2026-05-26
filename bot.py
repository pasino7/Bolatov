import os
import random
import sqlite3

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

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
# QUESTIONS (20 на каждый класс)
# =========================
question_bank = {

    "Информатика": {
        "5": [
            *[{"q": f"Информатика 5 класс вопрос {i+1}", "o": ["A", "B", "C", "D"], "a": "A"} for i in range(20)]
        ],
        "6": [
            *[{"q": f"Информатика 6 класс вопрос {i+1}", "o": ["A", "B", "C", "D"], "a": "A"} for i in range(20)]
        ],
        "7": [
            *[{"q": f"Информатика 7 класс вопрос {i+1}", "o": ["A", "B", "C", "D"], "a": "A"} for i in range(20)]
        ],
    },

    "Математика": {
        "5": [
            *[{"q": f"Математика 5 класс вопрос {i+1}", "o": ["1", "2", "3", "4"], "a": "1"} for i in range(20)]
        ],
        "6": [
            *[{"q": f"Математика 6 класс вопрос {i+1}", "o": ["1", "2", "3", "4"], "a": "1"} for i in range(20)]
        ],
        "7": [
            *[{"q": f"Математика 7 класс вопрос {i+1}", "o": ["1", "2", "3", "4"], "a": "1"} for i in range(20)]
        ],
    }
}

# =========================
# USER STATE
# =========================
user_state = {}

# =========================
# DB
# =========================
def add_user(user_id, username):
    cursor.execute("""
    INSERT OR IGNORE INTO users VALUES (?, ?, 0, 0, 0)
    """, (user_id, username))
    conn.commit()

def update_score(user_id, correct):
    if correct:
        cursor.execute("""
        UPDATE users SET score=score+1, correct_answers=correct_answers+1
        WHERE user_id=?
        """, (user_id,))
    else:
        cursor.execute("""
        UPDATE users SET wrong_answers=wrong_answers+1
        WHERE user_id=?
        """, (user_id,))
    conn.commit()

# =========================
# START (выбор предмета)
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)

    keyboard = [
        [InlineKeyboardButton("📘 Информатика", callback_data="sub_Информатика")],
        [InlineKeyboardButton("📗 Математика", callback_data="sub_Математика")]
    ]

    await update.message.reply_text(
        "Выбери предмет:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# HANDLER
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # =====================
    # SUBJECT SELECT
    # =====================
    if data.startswith("sub_"):
        subject = data.split("_")[1]

        user_state[user_id] = {"subject": subject}

        keyboard = [
            [InlineKeyboardButton("5 класс", callback_data="cls_5")],
            [InlineKeyboardButton("6 класс", callback_data="cls_6")],
            [InlineKeyboardButton("7 класс", callback_data="cls_7")]
        ]

        await query.message.reply_text(
            "Выбери класс:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # =====================
    # CLASS SELECT
    # =====================
    if data.startswith("cls_"):
        class_num = data.split("_")[1]

        subject = user_state[user_id]["subject"]

        pool = question_bank[subject][class_num]

        user_state[user_id].update({
            "class": class_num,
            "pool": random.sample(pool, len(pool)),
            "index": 0,
            "score_local": 0
        })

        await send_question(query.message, user_id)
        return

    # =====================
    # ANSWER
    # =====================
    if user_id in user_state and "pool" in user_state[user_id]:

        state = user_state[user_id]
        q = state["pool"][state["index"]]

        if data == q["a"]:
            update_score(user_id, True)
            state["score_local"] += 1
            await query.message.reply_text("✅ Верно!")
        else:
            update_score(user_id, False)
            await query.message.reply_text(f"❌ Неверно! Ответ: {q['a']}")

        state["index"] += 1
        await send_question(query.message, user_id)

# =========================
# SEND QUESTION
# =========================
async def send_question(message, user_id):

    state = user_state[user_id]
    i = state["index"]
    pool = state["pool"]

    # конец теста
    if i >= len(pool):

        await message.reply_text(
            f"🏁 Тест завершён!\n\n"
            f"📊 Правильных: {state['score_local']} из {len(pool)}"
        )
        return

    q = pool[i]

    keyboard = [[InlineKeyboardButton(o, callback_data=o)] for o in q["o"]]

    await message.reply_text(
        f"❓ {q['q']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
