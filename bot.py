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
                "options": [
                    "Электронное устройство",
                    "Игрушка",
                    "Телефон",
                    "Книга"
                ],
                "answer": "Электронное устройство"
            },

            {
                "question": "Что такое интернет?",
                "options": [
                    "Сеть",
                    "Игра",
                    "Файл",
                    "Папка"
                ],
                "answer": "Сеть"
            }
        ],

        "6": [
            {
                "question": "Что такое Windows?",
                "options": [
                    "Операционная система",
                    "Игра",
                    "Файл",
                    "Браузер"
                ],
                "answer": "Операционная система"
            }
        ],

        "7": [
            {
                "question": "Что такое Python?",
                "options": [
                    "Язык программирования",
                    "Игра",
                    "Файл",
                    "Монитор"
                ],
                "answer": "Язык программирования"
            }
        ]
    },

    "Математика": {

        "5": [
            {
                "question": "Сколько будет 2 + 2?",
                "options": [
                    "4",
                    "5",
                    "6",
                    "7"
                ],
                "answer": "4"
            }
        ],

        "6": [
            {
                "question": "Сколько будет 10 × 2?",
                "options": [
                    "20",
                    "15",
                    "30",
                    "40"
                ],
                "answer": "20"
            }
        ],

        "7": [
            {
                "question": "Чему равен корень из 49?",
                "options": [
                    "7",
                    "6",
                    "8",
                    "9"
                ],
                "answer": "7"
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

    with open(
        "results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Username",
            "Score",
            "Correct",
            "Wrong"
        ])

        writer.writerows(rows)

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    add_user(user.id, user.username)

    keyboard = [

        [
            InlineKeyboardButton(
                "Информатика",
                callback_data="Информатика"
            )
        ],

        [
            InlineKeyboardButton(
                "Математика",
                callback_data="Математика"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📚 Выберите предмет:",
        reply_markup=reply_markup
    )

# =========================
# BUTTON HANDLER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    text = query.data

    # =====================
    # SUBJECT
    # =====================

    if text in subjects:

        user_state[user_id] = {
            "subject": text
        }

        keyboard = []

        for class_name in subjects[text]:

            keyboard.append([
                InlineKeyboardButton(
                    class_name,
                    callback_data=class_name
                )
            ])

        await query.message.reply_text(
            "🏫 Выберите класс:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # =====================
    # CLASS
    # =====================

    if user_id in user_state:

        subject = user_state[user_id]["subject"]

        if text in subjects[subject]:

            user_state[user_id]["class"] = text

            await send_question(
                query.message,
                user_id
            )

            return

    # =====================
    # ANSWER
    # =====================

    if (
        user_id in user_state and
        "question" in user_state[user_id]
    ):

        q = user_state[user_id]["question"]

        if text == q["answer"]:

            update_score(user_id, True)

            await query.message.reply_text(
                "✅ Правильно!"
            )

        else:

            update_score(user_id, False)

            await query.message.reply_text(
                f"❌ Неправильно!\n"
                f"Правильный ответ: {q['answer']}"
            )

        await send_question(
            query.message,
            user_id
        )

# =========================
# SEND QUESTION
# =========================

async def send_question(message, user_id):

    subject = user_state[user_id]["subject"]
    class_name = user_state[user_id]["class"]

    q = random.choice(
        question_bank[subject][class_name]
    )

    user_state[user_id]["question"] = q

    keyboard = []

    for option in q["options"]:

        keyboard.append([
            InlineKeyboardButton(
                option,
                callback_data=option
            )
        ])

    await message.reply_text(
        f"❓ {q['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# RESULT
# =========================

async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    result_data = get_user_result(user_id)

    if not result_data:

        await update.message.reply_text(
            "Нет данных."
        )

        return

    score, correct, wrong = result_data

    total = correct + wrong

    percent = 0

    if total > 0:

        percent = round(
            (correct / total) * 100,
            2
        )

    text = (
        f"📊 Ваша статистика:\n\n"
        f"🏆 Баллы: {score}\n"
        f"✅ Правильных: {correct}\n"
        f"❌ Ошибок: {wrong}\n"
        f"📈 Процент: {percent}%"
    )

    await update.message.reply_text(text)

# =========================
# EXPORT
# =========================

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):

    export_results()

    await update.message.reply_document(
        document=open("results.csv", "rb")
    )

# =========================
# HELP
# =========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "📖 Команды бота:\n\n"
        "/start - запуск бота\n"
        "/result - статистика\n"
        "/export - экспорт CSV\n"
        "/help - помощь"
    )

    await update.message.reply_text(text)

# =========================
# MAIN
# =========================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("result", result)
    )

    app.add_handler(
        CommandHandler("export", export)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    print("Bot started")

    app.run_polling()

# =========================
# RUN
# =========================

if __name__ == "__main__":
    main()
