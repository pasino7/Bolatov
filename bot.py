import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

subjects = {
    "Информатика": ["5", "6", "7", "8", "9", "10", "11"],
    "Математика": ["5", "6", "7", "8", "9", "10", "11"]
}

question_bank = {
    "Информатика": {
        "5": [
            {"question": "Что такое компьютер?", "options": ["Электронное устройство", "Игрушка", "Телефон", "Книга"], "answer": "Электронное устройство"},
            {"question": "Что такое интернет?", "options": ["Сеть", "Игра", "Файл", "Папка"], "answer": "Сеть"},
            {"question": "Что делает мышь?", "options": ["Управляет курсором", "Печатает", "Сканирует", "Считает"], "answer": "Управляет курсором"},
            {"question": "Что такое монитор?", "options": ["Экран", "Принтер", "Клавиатура", "Мышь"], "answer": "Экран"},
            {"question": "Что такое клавиатура?", "options": ["Устройство ввода", "Экран", "Программа", "Файл"], "answer": "Устройство ввода"},
            {"question": "Что хранит компьютер?", "options": ["Данные", "Игры", "Книги", "Людей"], "answer": "Данные"},
            {"question": "Что такое файл?", "options": ["Данные", "Монитор", "Игра", "Кнопка"], "answer": "Данные"},
            {"question": "Что такое папка?", "options": ["Хранилище файлов", "Игра", "Монитор", "Клавиша"], "answer": "Хранилище файлов"},
            {"question": "Что делает принтер?", "options": ["Печатает", "Сканирует", "Удаляет", "Копирует"], "answer": "Печатает"},
            {"question": "Что такое пароль?", "options": ["Защита", "Игра", "Файл", "Кнопка"], "answer": "Защита"}
        ],
        "6": [
            {"question": "Что такое Windows?", "options": ["ОС", "Игра", "Файл", "Браузер"], "answer": "ОС"},
            {"question": "Что делает Ctrl+C?", "options": ["Копирует", "Удаляет", "Печатает", "Закрывает"], "answer": "Копирует"},
            {"question": "Что делает Ctrl+V?", "options": ["Вставляет", "Удаляет", "Копирует", "Закрывает"], "answer": "Вставляет"},
            {"question": "Что такое файл?", "options": ["Данные", "Игра", "Монитор", "Клавиатура"], "answer": "Данные"},
            {"question": "Что такое папка?", "options": ["Хранилище", "Игра", "Монитор", "Кнопка"], "answer": "Хранилище"},
            {"question": "Что делает мышь?", "options": ["Управляет", "Печатает", "Сканирует", "Удаляет"], "answer": "Управляет"},
            {"question": "Что такое браузер?", "options": ["Интернет программа", "Игра", "Файл", "Папка"], "answer": "Интернет программа"},
            {"question": "Что такое интернет?", "options": ["Сеть", "Игра", "Файл", "Монитор"], "answer": "Сеть"},
            {"question": "Что такое YouTube?", "options": ["Видео сервис", "Игра", "Файл", "Папка"], "answer": "Видео сервис"},
            {"question": "Что такое вирус?", "options": ["Опасная программа", "Игра", "Файл", "Монитор"], "answer": "Опасная программа"}
        ],
        "7": [
            {"question": "Что такое Python?", "options": ["Язык", "Игра", "Файл", "Монитор"], "answer": "Язык"},
            {"question": "Что делает print()?", "options": ["Вывод", "Удаление", "Копирование", "Создание"], "answer": "Вывод"},
            {"question": "Что такое переменная?", "options": ["Хранилище", "Игра", "Файл", "Монитор"], "answer": "Хранилище"},
            {"question": "Что такое цикл?", "options": ["Повторение", "Файл", "Монитор", "Игра"], "answer": "Повторение"},
            {"question": "Что такое if?", "options": ["Условие", "Цикл", "Файл", "Монитор"], "answer": "Условие"},
            {"question": "Что такое input()?", "options": ["Ввод", "Вывод", "Удаление", "Копирование"], "answer": "Ввод"},
            {"question": "Что такое int?", "options": ["Число", "Текст", "Логика", "Файл"], "answer": "Число"},
            {"question": "Что такое str?", "options": ["Текст", "Число", "Файл", "Монитор"], "answer": "Текст"},
            {"question": "Что такое bool?", "options": ["Логика", "Число", "Текст", "Файл"], "answer": "Логика"},
            {"question": "Что делает len()?", "options": ["Считает", "Удаляет", "Копирует", "Создает"], "answer": "Считает"}
        ],
        "8": [
            {"question": "Что такое алгоритм?", "options": ["План", "Игра", "Файл", "Монитор"], "answer": "План"},
            {"question": "Что такое массив?", "options": ["Список", "Число", "Текст", "Файл"], "answer": "Список"},
            {"question": "Что такое функция?", "options": ["Блок кода", "Игра", "Файл", "Монитор"], "answer": "Блок кода"},
            {"question": "Что делает return?", "options": ["Возвращает", "Удаляет", "Создает", "Печатает"], "answer": "Возвращает"},
            {"question": "Что такое библиотека?", "options": ["Набор функций", "Игра", "Файл", "Монитор"], "answer": "Набор функций"},
            {"question": "Что такое класс?", "options": ["Шаблон", "Игра", "Файл", "Монитор"], "answer": "Шаблон"},
            {"question": "Что такое объект?", "options": ["Экземпляр", "Игра", "Файл", "Монитор"], "answer": "Экземпляр"},
            {"question": "Что такое API?", "options": ["Интерфейс", "Игра", "Файл", "Монитор"], "answer": "Интерфейс"},
            {"question": "Что такое база данных?", "options": ["Хранилище", "Игра", "Монитор", "Файл"], "answer": "Хранилище"},
            {"question": "Что такое сервер?", "options": ["Компьютер", "Игра", "Файл", "Монитор"], "answer": "Компьютер"}
        ]
        # (9–11 добавлю дальше если скажешь)
    }
}

user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Информатика", "Математика"]]
    await update.message.reply_text("Выбери предмет:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text in subjects:
        user_state[user_id] = {"subject": text}
        keyboard = [[c] for c in subjects[text]]
        await update.message.reply_text("Выбери класс:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if user_id in user_state and "class" not in user_state[user_id]:
        subject = user_state[user_id]["subject"]
        if text in subjects[subject]:
            user_state[user_id]["class"] = text
            q = random.choice(question_bank[subject][text])
            user_state[user_id]["question"] = q
            keyboard = [[o] for o in q["options"]]
            await update.message.reply_text(q["question"], reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if user_id in user_state and "question" in user_state[user_id]:
        q = user_state[user_id]["question"]
        if text == q["answer"]:
            await update.message.reply_text("✅ Правильно!")
        else:
            await update.message.reply_text(f"❌ Неправильно! Ответ: {q['answer']}")

        subject = user_state[user_id]["subject"]
        class_ = user_state[user_id]["class"]
        q = random.choice(question_bank[subject][class_])
        user_state[user_id]["question"] = q

        keyboard = [[o] for o in q["options"]]
        await update.message.reply_text(q["question"], reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    print("Bot started")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
