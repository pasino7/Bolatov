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
# QUESTIONS (РАСШИРЕННЫЕ)
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
            },
            {
                "question": "Что делает мышь?",
                "options": ["Управляет курсором", "Печатает", "Сохраняет", "Удаляет"],
                "answer": "Управляет курсором"
            },
            {
                "question": "Что такое файл?",
                "options": ["Хранилище информации", "Монитор", "Процессор", "Сайт"],
                "answer": "Хранилище информации"
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
            },
            {
                "question": "Что такое антивирус?",
                "options": ["Защита от вирусов", "Игра", "ОС", "Файл"],
                "answer": "Защита от вирусов"
            },
            {
                "question": "Что такое сервер?",
                "options": ["Компьютер для хранения данных", "Монитор", "Принтер", "Мышь"],
                "answer": "Компьютер для хранения данных"
            }
        ],

        "7": [
            {
                "question": "Что такое Python?",
                "options": ["Язык программирования", "Игра", "Файл", "Монитор"],
                "answer": "Язык программирования"
            },
            {
                "question": "Что такое переменная?",
                "options": ["Хранение данных", "Ошибка", "Экран", "Файл"],
                "answer": "Хранение данных"
            },
            {
                "question": "Что делает цикл?",
                "options": ["Повторяет действия", "Удаляет файлы", "Выключает ПК", "Открывает сайт"],
                "answer": "Повторяет действия"
            },
            {
                "question": "Что такое алгоритм?",
                "options": ["Последовательность действий", "Файл", "Игра", "Вирус"],
                "answer": "Последовательность действий"
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
            },
            {
                "question": "Сколько будет 9 - 3?",
                "options": ["6", "5", "7", "8"],
                "answer": "6"
            },
            {
                "question": "Сколько будет 10 - 4?",
                "options": ["6", "5", "7", "8"],
                "answer": "6"
            }
        ],

        "6": [
            {
                "question": "Сколько будет 10 × 2?",
                "options": ["20", "15", "30", "40"],
                "answer": "20"
            },
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
                "question": "Чему равен корень из 49?",
                "options": ["7", "6", "8", "9"],
                "answer": "7"
            },
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
# DATABASE FUNCTIONS
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
# EXPORT CSV
# =========================

def export_results():

    cursor.execute("""
    SELECT username, score, correct_answers, wrong_answers
    FROM users
    """)

    rows = cursor.fetchall()

    with open("results.csv", "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow(["Username", "Score", "Correct", "Wrong"])

        writer.writerows(rows)

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

    if user_id in user_state:

        subject = user_state[user_id]["subject"]

        if text in subjects[subject]:

            user_state[user_id]["class"] = text

            await send_question(query.message, user_id)
            return

    if user_id in user_state and "question" in user_state[user_id]:

        q = user_state[user_id]["question"]

        if text == q["answer"]:
            update_score(user_id, True)
            await query.message.reply_text("✅ Правильно!")
        else:
            update_score(user_id, False)
            await query.message.reply_text(f"❌ Неправильно!\nПравильный ответ: {q['answer']}")

        await send_question(query.message, user_id)

# =========================
# SEND QUESTION
# =========================

async def send_question(message, user_id):

    subject = user_state[user_id]["subject"]
    class_name = user_state[user_id]["class"]

    q = random.choice(question_bank[subject][class_name])

    user_state[user_id]["question"] = q

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=opt)]
        for opt in q["options"]
    ]

    await message.reply_text(
        f"❓ {q['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# RESULT
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

    export_results()

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
