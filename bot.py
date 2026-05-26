import os
import random
import sqlite3

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from openpyxl import Workbook

TOKEN = os.environ.get("TOKEN")

# =========================
# ADMIN SAFE
# =========================
raw_admins = os.environ.get("ADMIN_IDS", "")

ADMIN_IDS = (
    list(map(int, raw_admins.split(",")))
    if raw_admins.strip()
    else []
)

def is_admin(user_id):
    return user_id in ADMIN_IDS

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
# QUESTION BANK (20 ВОПРОСОВ НА КЛАСС)
# =========================
question_bank = {

    "Информатика": {

        "5": [
            {"q": "Что такое компьютер?", "o": ["Устройство для обработки информации", "Игрушка", "Книга", "Телевизор"], "a": "Устройство для обработки информации"},
            {"q": "Что такое интернет?", "o": ["Сеть", "Игра", "Файл", "Книга"], "a": "Сеть"},
            {"q": "Что делает клавиатура?", "o": ["Ввод текста", "Вывод звука", "Печать", "Хранение"], "a": "Ввод текста"},
            {"q": "Что такое монитор?", "o": ["Экран", "Мышь", "Клавиатура", "Принтер"], "a": "Экран"},
            {"q": "Что такое мышь?", "o": ["Устройство управления", "Экран", "Файл", "Папка"], "a": "Устройство управления"},
            {"q": "Что такое файл?", "o": ["Данные", "Монитор", "Мышь", "Клавиатура"], "a": "Данные"},
            {"q": "Что такое папка?", "o": ["Хранилище файлов", "Игра", "Экран", "Книга"], "a": "Хранилище файлов"},
            {"q": "Что такое процессор?", "o": ["Мозг компьютера", "Экран", "Мышь", "Файл"], "a": "Мозг компьютера"},
            {"q": "Что такое программа?", "o": ["Набор команд", "Игра", "Книга", "Экран"], "a": "Набор команд"},
            {"q": "Что такое Windows?", "o": ["ОС", "Игра", "Файл", "Браузер"], "a": "ОС"},
            {"q": "Что такое иконка?", "o": ["Значок", "Файл", "Папка", "Кнопка"], "a": "Значок"},
            {"q": "Что такое меню?", "o": ["Список команд", "Игра", "Книга", "Файл"], "a": "Список команд"},
            {"q": "Что такое браузер?", "o": ["Интернет программа", "Игра", "Книга", "Файл"], "a": "Интернет программа"},
            {"q": "Что такое USB?", "o": ["Порт", "Игра", "Монитор", "Файл"], "a": "Порт"},
            {"q": "Что такое сеть?", "o": ["Соединение устройств", "Книга", "Игра", "Файл"], "a": "Соединение устройств"},
            {"q": "Что такое принтер?", "o": ["Печатает", "Играет", "Удаляет", "Хранит"], "a": "Печатает"},
            {"q": "Что такое антивирус?", "o": ["Защита", "Игра", "Файл", "Экран"], "a": "Защита"},
            {"q": "Что такое рабочий стол?", "o": ["Главный экран", "Папка", "Файл", "Игра"], "a": "Главный экран"},
            {"q": "Что делает CPU?", "o": ["Обрабатывает данные", "Печатает", "Стирает", "Играет"], "a": "Обрабатывает данные"},
            {"q": "Что такое данные?", "o": ["Информация", "Игра", "Книга", "Экран"], "a": "Информация"}
        ],

        "6": [
            {"q": "Что такое HTML?", "o": ["Язык разметки", "Игра", "Файл", "ОС"], "a": "Язык разметки"},
            {"q": "Что такое CSS?", "o": ["Стили", "Игра", "Файл", "ОС"], "a": "Стили"},
            {"q": "Что такое JavaScript?", "o": ["Язык программирования", "Игра", "Файл", "ОС"], "a": "Язык программирования"},
            {"q": "Что такое сайт?", "o": ["Страница", "Игра", "Файл", "ОС"], "a": "Страница"},
            {"q": "Что такое сервер?", "o": ["Компьютер", "Игра", "Файл", "ОС"], "a": "Компьютер"},
            {"q": "Что такое база данных?", "o": ["Хранилище", "Игра", "Файл", "ОС"], "a": "Хранилище"},
            {"q": "Что такое IP?", "o": ["Адрес", "Игра", "Файл", "ОС"], "a": "Адрес"},
            {"q": "Что такое Wi-Fi?", "o": ["Сеть", "Игра", "Файл", "ОС"], "a": "Сеть"},
            {"q": "Что такое вирус?", "o": ["Вредоносная программа", "Игра", "Файл", "ОС"], "a": "Вредоносная программа"},
            {"q": "Что такое облако?", "o": ["Хранение данных", "Игра", "Файл", "ОС"], "a": "Хранение данных"},
            {"q": "Что такое Excel?", "o": ["Таблица", "Игра", "Файл", "ОС"], "a": "Таблица"},
            {"q": "Что такое Word?", "o": ["Текст", "Игра", "Файл", "ОС"], "a": "Текст"},
            {"q": "Что такое Git?", "o": ["Контроль версий", "Игра", "Файл", "ОС"], "a": "Контроль версий"},
            {"q": "Что такое FTP?", "o": ["Передача файлов", "Игра", "Файл", "ОС"], "a": "Передача файлов"},
            {"q": "Что такое DNS?", "o": ["Домены", "Игра", "Файл", "ОС"], "a": "Домены"},
            {"q": "Что такое кэш?", "o": ["Память", "Игра", "Файл", "ОС"], "a": "Память"},
            {"q": "Что такое API?", "o": ["Интерфейс", "Игра", "Файл", "ОС"], "a": "Интерфейс"},
            {"q": "Что такое протокол?", "o": ["Правила", "Игра", "Файл", "ОС"], "a": "Правила"},
            {"q": "Что такое VPN?", "o": ["Защищённая сеть", "Игра", "Файл", "ОС"], "a": "Защищённая сеть"},
            {"q": "Что такое резервная копия?", "o": ["Backup", "Игра", "Файл", "ОС"], "a": "Backup"}
        ],

        "7": [
            {"q": "Что такое Python?", "o": ["Язык программирования", "Игра", "Файл", "ОС"], "a": "Язык программирования"},
            {"q": "Что такое переменная?", "o": ["Хранение данных", "Игра", "Файл", "ОС"], "a": "Хранение данных"},
            {"q": "Что такое цикл?", "o": ["Повтор действий", "Игра", "Файл", "ОС"], "a": "Повтор действий"},
            {"q": "Что такое функция?", "o": ["Блок кода", "Игра", "Файл", "ОС"], "a": "Блок кода"},
            {"q": "Что такое список?", "o": ["Набор элементов", "Игра", "Файл", "ОС"], "a": "Набор элементов"},
            {"q": "Что такое условие?", "o": ["if", "Игра", "Файл", "ОС"], "a": "if"},
            {"q": "Что такое класс?", "o": ["Шаблон", "Игра", "Файл", "ОС"], "a": "Шаблон"},
            {"q": "Что такое объект?", "o": ["Экземпляр", "Игра", "Файл", "ОС"], "a": "Экземпляр"},
            {"q": "Что такое библиотека?", "o": ["Функции", "Игра", "Файл", "ОС"], "a": "Функции"},
            {"q": "Что такое баг?", "o": ["Ошибка", "Игра", "Файл", "ОС"], "a": "Ошибка"},
            {"q": "Что такое отладка?", "o": ["Debug", "Игра", "Файл", "ОС"], "a": "Debug"},
            {"q": "Что такое алгоритм?", "o": ["План", "Игра", "Файл", "ОС"], "a": "План"},
            {"q": "Что такое IDE?", "o": ["Среда разработки", "Игра", "Файл", "ОС"], "a": "Среда разработки"},
            {"q": "Что такое компилятор?", "o": ["Перевод кода", "Игра", "Файл", "ОС"], "a": "Перевод кода"},
            {"q": "Что такое массив?", "o": ["Структура данных", "Игра", "Файл", "ОС"], "a": "Структура данных"},
            {"q": "Что такое рекурсия?", "o": ["Функция себя вызывает", "Игра", "Файл", "ОС"], "a": "Функция себя вызывает"},
            {"q": "Что такое API?", "o": ["Интерфейс", "Игра", "Файл", "ОС"], "a": "Интерфейс"},
            {"q": "Что такое JSON?", "o": ["Формат данных", "Игра", "Файл", "ОС"], "a": "Формат данных"},
            {"q": "Что такое сервер?", "o": ["Машина данных", "Игра", "Файл", "ОС"], "a": "Машина данных"},
            {"q": "Что такое Git?", "o": ["Контроль версий", "Игра", "Файл", "ОС"], "a": "Контроль версий"}
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
# EXCEL
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
# QUIZ
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("sub_"):
        user_state[user_id] = {"subject": "Информатика"}

        keyboard = [
            [InlineKeyboardButton("5 класс", callback_data="cls_5")],
            [InlineKeyboardButton("6 класс", callback_data="cls_6")],
            [InlineKeyboardButton("7 класс", callback_data="cls_7")]
        ]

        await query.message.reply_text("Выбери класс:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("cls_"):
        class_num = data.replace("cls_", "")

        subject = "Информатика"
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
            await query.message.reply_text(f"❌ Неверно! Ответ: {q['a']}")

        state["index"] += 1
        await send_question(query.message, user_id)

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
# ADMIN PANEL
# =========================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ Нет доступа")
        return

    keyboard = [
        ["📊 Статистика"],
        ["📁 Excel отчет"],
        ["🏆 Топ пользователей"]
    ]

    await update.message.reply_text(
        "👨‍🏫 Админ панель:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# =========================
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    text = update.message.text

    if not is_admin(user_id):
        return

    if text == "📊 Статистика":
        cursor.execute("SELECT COUNT(*), SUM(score) FROM users")
        data = cursor.fetchone()
        await update.message.reply_text(f"👥 Пользователей: {data[0]}\n🏆 Баллы: {data[1]}")

    elif text == "📁 Excel отчет":
        export_excel()
        await update.message.reply_document(open("results.xlsx", "rb"))

    elif text == "🏆 Топ пользователей":
        cursor.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 10")
        top = cursor.fetchall()

        text_top = "🏆 ТОП:\n\n"
        for i, row in enumerate(top, 1):
            text_top += f"{i}. {row[0]} — {row[1]}\n"

        await update.message.reply_text(text_top)

# =========================
# MAIN
# =========================
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_buttons))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
