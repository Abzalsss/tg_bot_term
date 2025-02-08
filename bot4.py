import json
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Состояния бота
WAITING_FOR_TERM = 1
WAITING_FOR_LETTER = 2


# Загрузка данных
def load_data():
    with open('it_terms.json', 'r', encoding='utf-8') as file:
        return json.load(file)["terms"]


data = load_data()


# Главное меню с кнопками
def main_menu():
    keyboard = [["📘 Найти термин", "🔠 Термины на букву"],
                ["🎲 Случайный термин", "ℹ️ Помощь"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


# Команда /start
async def start(update: Update, context: CallbackContext):
    # Путь к файлу изображения
    photo_path = 'start.png'

    # Отправка изображения
    with open(photo_path, 'rb') as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=(
                "📚 *Добро пожаловать в бот-справочник по IT-терминам!* 👋\n\n"
                "Здесь вы можете:\n"
                "🔹 Найти определение нужного термина\n"
                "🔹 Ознакомиться с терминами на выбранную букву\n"
                "🔹 Получить случайный IT-термин для изучения\n\n"
                "Выберите нужный раздел и начнём! 🚀"
            ),
            parse_mode="Markdown",
            reply_markup=main_menu()
        )



# Команда /help
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Привет! 👋 Добро пожаловать в бота по IT-терминам!\n\n"
        "👇 Вот что я умею: \n"
        "📘 Найти термин – отправьте название термина, и я расскажу о нём.\n"
        "🔠 Термины на букву – выберите букву, чтобы увидеть все термины, начинающиеся с неё.\n"
        "🎲 Случайный термин – получите случайный IT-термин и его описание.\n\n"
        "❓ Если у вас возникли вопросы или проблемы, напишите в техподдержку: @bstrbzl или zzz!.\n\n"
        "😊 Используйте команды и узнайте больше об IT!"
    )


# Вход в режим поиска термина
async def start_term_search(update: Update, context: CallbackContext):
    await update.message.reply_text("🔍 Введите название термина или нажмите '⬅️ Назад'",
                                    reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True,
                                                                     one_time_keyboard=True))
    return WAITING_FOR_TERM


# Поиск термина
async def search_term(update: Update, context: CallbackContext):
    term = update.message.text.lower()

    for letter, terms in data.items():
        for item in terms:
            if item["term"].lower() == term:
                await update.message.reply_text(f"{item['term']}: {item.get('definition', 'Нет описания')}")
                return WAITING_FOR_TERM

    await update.message.reply_text("❌ Термин не найден. Попробуйте другой.")
    return WAITING_FOR_TERM


async def exit_term_search(update: Update, context: CallbackContext):
    await update.message.reply_text("🔍 Вы вышли из поиска.", reply_markup=main_menu())
    return ConversationHandler.END


# Вход в режим поиска по букве
async def start_letter_search(update: Update, context: CallbackContext):
    await update.message.reply_text("🔍 Введите букву или нажмите '⬅️ Назад'",
                                    reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True,
                                                                     one_time_keyboard=True))
    return WAITING_FOR_LETTER


# Поиск по букве
async def search_by_letter(update: Update, context: CallbackContext):
    letter = update.message.text.strip().upper()

    if letter in data and data[letter]:
        terms_list = "\n".join([item["term"] for item in data[letter]])
        await update.message.reply_text(f"Термины на '{letter}':\n{terms_list}")
    else:
        await update.message.reply_text(f"❌ Терминов на букву '{letter}' нет.")
    return WAITING_FOR_LETTER


async def exit_letter_search(update: Update, context: CallbackContext):
    await update.message.reply_text("Вы вышли из поиска.", reply_markup=main_menu())
    return ConversationHandler.END


# Случайный термин
async def random_term(update: Update, context: CallbackContext):
    valid_letters = [letter for letter in data.keys() if data[letter]]
    if not valid_letters:
        await update.message.reply_text("Нет данных для случайного термина.")
        return
    random_letter = random.choice(valid_letters)
    random_item = random.choice(data[random_letter])
    await update.message.reply_text(f"{random_item['term']}: {random_item.get('definition', 'Нет описания')}")


# Запуск бота
def main():
    token = "8190966734:AAH5lCuJQURW6kWG4uKve2ax0-RRCbxfiiY"
    app = Application.builder().token(token).build()

    term_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("📘 Найти термин"), start_term_search)],
        states={WAITING_FOR_TERM: [MessageHandler(filters.TEXT & ~filters.Regex("⬅️ Назад"), search_term)]},
        fallbacks=[MessageHandler(filters.Regex("⬅️ Назад"), lambda u, c: exit_term_search(u, c))]
    )

    letter_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("🔠 Термины на букву"), start_letter_search)],
        states={WAITING_FOR_LETTER: [MessageHandler(filters.TEXT & ~filters.Regex("⬅️ Назад"), search_by_letter)]},
        fallbacks=[MessageHandler(filters.Regex("⬅️ Назад"), lambda u, c: exit_letter_search(u, c))]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("ℹ️ Помощь"), help_command))
    app.add_handler(term_handler)
    app.add_handler(letter_handler)
    app.add_handler(MessageHandler(filters.Regex("🎲 Случайный термин"), random_term))

    app.run_polling()


if __name__ == "__main__":
    main()
