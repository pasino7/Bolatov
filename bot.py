import os
import random
import sqlite3
import csv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# =========================
# TOKEN
# =========================

TOKEN = os.getenv("TOKEN")

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
# SUBJECTS
# =========================

subjects = {
    "Информатика": ["5", "6", "7"],
    "Математика": ["5", "6", "7"]
}

# =========================
# QUESTIONS
# =========================

question_bank = {
    "Информатика": {
        "5": [
            {
                "question": "Что такое компьютер?",
                "options": ["Электронное устройство", "Игрушка", "Телефон", "Книга"],
                "answer": "Электронное устройство"
            },
            {
                "question": "Что такое интернет?",
                "options": ["Сеть", "Игра", "Файл", "Папка"],
                "answer": "Сеть"
            },
            {
                "question": "Что делает клавиатура?",
                "options": ["Устройство ввода", "Экран", "Принтер", "Память"],
                "answer": "Устройство ввода"
            }
        ],

        "6": [
            {
                "question": "Что такое Windows?",
                "options": ["Операционная система", "Игра", "Файл", "Браузер"],
                "answer": "Операционная система"
            },
            {
                "question": "Что такое браузер?",
                "options": ["Программа для интернета", "Игра", "Файл", "Антивирус"],
                "answer": "Программа для интернета"
            }
        ],

        "7": [
            {
                "question": "Что такое Python?",
                "options": ["Язык программирования", "Игра", "Файл", "Монитор"],
                "answer": "Язык программирования"
            },
            {
                "question": "Что такое цикл?",
                "options": ["Повтор действий", "Удаление файлов", "Экран", "Вирус"],
                "answer": "Повтор действий"
            }
        ]
    },

    "Математика": {
        "5": [
            {
                "question": "Сколько будет 2 + 2?",
                "options": ["4", "5", "6", "7"],
                "answer": "4"
            },
            {
                "question": "Сколько будет 5 + 7?",
                "options": ["12", "11", "13", "10"],
                "answer": "12"
            }
        ],

        "6": [
            {
                "question": "Сколько будет 3 × 4?",
                "options": ["12", "10", "14", "11"],
                "answer": "12"
            },
            {
                "question": "Сколько будет 18 ÷ 2?",
                "options": ["9", "8", "7", "10"],
                "answer": "9"
            }
        ],

        "7": [
            {
                "question": "Чему равно 2²?",
                "options": ["4", "2", "6", "8"],
                "answer": "4"
            },
            {
                "question": "Чему равно 3²?",
                "options": ["9", "6", "12", "8"],
                "answer": "9"
            }
        ]
    }
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
    INSERT OR IGNORE INTO users
    (user_id, username, score, correct_answers, wrong_answers)
    VALUES (?, ?, 0, 0, 0)
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


def get_user_result(user_id):
    cursor.execute("""
    SELECT score, correct_answers, wrong_answers
    FROM users
    WHERE user_id = ?
    """, (user_id,))
    return cursor.fetchone()

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    add_user(user.id, user.username)

    keyboard = [
        [InlineKeyboardButton("Информатика", callback_data="Информатика")],
        [InlineKeyboardButton("Математика", callback_data="Математика")]
    ]

    await update.message.reply_text(
        "📚 Выберите предмет:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# BUTTON HANDLER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    text = query.data

    # выбор предмета
    if text in subjects:
        user_state[user_id] = {"subject": text}
        keyboard = [
            [InlineKeyboardButton(c, callback_data=c)]
            for c in subjects[text]
        ]

        await query.message.reply_text(
            "🏫 Выберите класс:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # выбор класса
    if user_id in user_state and text in subjects[user_state[user_id]["subject"]]:

        subject = user_state[user_id]["subject"]

        # 🎯 СОЗДАЁМ ПУЛ ВОПРОСОВ (ВАЖНО)
        pool = question_bank[subject][text]
        random.shuffle(pool)

        user_state[user_id]["class"] = text
        user_state[user_id]["pool"] = pool
        user_state[user_id]["index"] = 0

        await send_question(query.message, user_id)
        return

    # ответ
    if user_id in user_state and "pool" in user_state[user_id]:

        q = user_state[user_id]["pool"][user_state[user_id]["index"]]

        if text == q["answer"]:
            update_score(user_id, True)
            await query.message.reply_text("✅ Правильно!")
        else:
            update_score(user_id, False)
            await query.message.reply_text(f"❌ Неправильно!\nПравильный ответ: {q['answer']}")

        user_state[user_id]["index"] += 1

        await send_question(query.message, user_id)

# =========================
# SEND QUESTION
# =========================

async def send_question(message, user_id):

    index = user_state[user_id]["index"]
    pool = user_state[user_id]["pool"]

    # 🏁 КОНЕЦ ТЕСТА
    if index >= len(pool):

        result_data = get_user_result(user_id)
        score, correct, wrong = result_data

        total = correct + wrong
        percent = round((correct / total) * 100, 2) if total > 0 else 0

        await message.reply_text(
            "🏁 ТЕСТ ЗАВЕРШЁН!\n\n"
            f"🏆 Баллы: {score}\n"
            f"✅ Правильных: {correct}\n"
            f"❌ Ошибок: {wrong}\n"
            f"📈 Процент: {percent}%"
        )
        return

    q = pool[index]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=opt)]
        for opt in q["options"]
    ]

    await message.reply_text(
        f"❓ {q['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# RESULT COMMAND
# =========================

async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    data = get_user_result(user_id)

    if not data:
        await update.message.reply_text("Нет данных.")
        return

    score, correct, wrong = data
    total = correct + wrong

    percent = round((correct / total) * 100, 2) if total > 0 else 0

    await update.message.reply_text(
        f"📊 Статистика:\n\n"
        f"🏆 Баллы: {score}\n"
        f"✅ Правильных: {correct}\n"
        f"❌ Ошибок: {wrong}\n"
        f"📈 Процент: {percent}%"
    )

# =========================
# EXPORT
# =========================

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("""
    SELECT username, score, correct_answers, wrong_answers
    FROM users
    """)

    rows = cursor.fetchall()

    with open("results.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Score", "Correct", "Wrong"])
        writer.writerows(rows)

    await update.message.reply_document(open("results.csv", "rb"))

# =========================
# MAIN
# =========================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("result", result))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
