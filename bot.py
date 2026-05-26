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

from openpyxl import Workbook

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

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
# QUESTION BANK (НЕ МЕНЯЛ)
# =========================
question_bank = {
    "Информатика": {
        "5": [
            {"q": "Что такое компьютер?", "o": ["Устройство для обработки информации", "Игрушка", "Книга", "Телевизор"], "a": "Устройство для обработки информации"},
            {"q": "Что такое интернет?", "o": ["Сеть", "Игра", "Файл", "Книга"], "a": "Сеть"},
            {"q": "Что такое клавиатура?", "o": ["Устройство ввода", "Экран", "Принтер", "Колонка"], "a": "Устройство ввода"},
            {"q": "Что делает мышь?", "o": ["Управляет курсором", "Печатает", "Удаляет", "Сканирует"], "a": "Управляет курсором"},
            {"q": "Что такое монитор?", "o": ["Экран", "Мышь", "Клавиатура", "Файл"], "a": "Экран"},
            {"q": "Что такое файл?", "o": ["Данные", "Монитор", "Игра", "Книга"], "a": "Данные"},
            {"q": "Что такое папка?", "o": ["Хранилище файлов", "Игра", "Экран", "Кнопка"], "a": "Хранилище файлов"},
            {"q": "Что такое процессор?", "o": ["Мозг компьютера", "Экран", "Мышь", "Файл"], "a": "Мозг компьютера"},
            {"q": "Что такое программа?", "o": ["Набор команд", "Файл", "Книга", "Игра"], "a": "Набор команд"},
            {"q": "Что такое Windows?", "o": ["ОС", "Игра", "Файл", "Браузер"], "a": "ОС"},
            {"q": "Что такое иконка?", "o": ["Значок программы", "Файл", "Папка", "Экран"], "a": "Значок программы"},
            {"q": "Что такое меню?", "o": ["Список команд", "Игра", "Файл", "Книга"], "a": "Список команд"},
            {"q": "Что такое браузер?", "o": ["Программа для интернета", "Игра", "Файл", "Книга"], "a": "Программа для интернета"},
            {"q": "Что такое USB?", "o": ["Порт подключения", "Игра", "Монитор", "Файл"], "a": "Порт подключения"},
            {"q": "Что такое сеть?", "o": ["Соединение устройств", "Книга", "Игра", "Экран"], "a": "Соединение устройств"},
            {"q": "Что такое принтер?", "o": ["Печатает документы", "Стирает", "Играет", "Хранит"], "a": "Печатает документы"},
            {"q": "Что такое файл изображения?", "o": ["Картинка", "Текст", "Программа", "Игра"], "a": "Картинка"},
            {"q": "Что такое антивирус?", "o": ["Защита от вирусов", "Игра", "Файл", "Экран"], "a": "Защита от вирусов"},
            {"q": "Что такое рабочий стол?", "o": ["Главный экран ПК", "Папка", "Файл", "Игра"], "a": "Главный экран ПК"},
            {"q": "Что делает CPU?", "o": ["Обрабатывает данные", "Печатает", "Хранит", "Удаляет"], "a": "Обрабатывает данные"}
        ]
    }
}

# =========================
# STATE
# =========================
user_state = {}

# =========================
# DB
# =========================
def add_user(user_id, username):
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, 0, 0, 0)", (user_id, username))
    conn.commit()

def update_score(user_id, correct):
    if correct:
        cursor.execute("UPDATE users SET score=score+1, correct_answers=correct_answers+1 WHERE user_id=?", (user_id,))
    else:
        cursor.execute("UPDATE users SET wrong_answers=wrong_answers+1 WHERE user_id=?", (user_id,))
    conn.commit()

# =========================
# ADMIN CHECK
# =========================
def is_admin(user_id):
    return user_id == ADMIN_ID

# =========================
# EXPORT EXCEL
# =========================
def export_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    ws.append(["Username", "Score", "Correct", "Wrong"])

    cursor.execute("SELECT username, score, correct_answers, wrong_answers FROM users")
    for row in cursor.fetchall():
        ws.append(row)

    wb.save("results.xlsx")

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    add_user(user.id, user.username)

    keyboard = [
        [InlineKeyboardButton("📘 Информатика", callback_data="sub_Информатика")]
    ]

    await update.message.reply_text(
        "📚 Выбери предмет:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# BUTTON
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("sub_"):
        subject = data.replace("sub_", "")

        user_state[user_id] = {"subject": subject}

        keyboard = [
            [InlineKeyboardButton("5 класс", callback_data="cls_5")]
        ]

        await query.message.reply_text("Выбери класс:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("cls_"):
        class_num = data.replace("cls_", "")
        subject = user_state[user_id]["subject"]

        pool = question_bank[subject][class_num]

        user_state[user_id] = {
            "subject": subject,
            "class": class_num,
            "pool": random.sample(pool, len(pool)),
            "index": 0,
            "score_local": 0
        }

        await send_question(query.message, user_id)
        return

    if user_id in user_state:
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
# QUESTION
# =========================
async def send_question(message, user_id):

    state = user_state[user_id]
    i = state["index"]
    pool = state["pool"]

    if i >= len(pool):
        await message.reply_text(
            f"🏁 Тест завершён!\n📊 Правильных: {state['score_local']}/{len(pool)}"
        )
        return

    q = pool[i]

    keyboard = [[InlineKeyboardButton(o, callback_data=o)] for o in q["o"]]

    await message.reply_text(f"❓ {q['q']}", reply_markup=InlineKeyboardMarkup(keyboard))

# =========================
# EXPORT COMMAND (ADMIN)
# =========================
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ Нет доступа")
        return

    export_excel()

    await update.message.reply_document(
        document=open("results.xlsx", "rb")
    )

# =========================
# MAIN
# =========================
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
