from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "ВСТАВЬ_СЮДА_TOKEN_ОТ_BOTFATHER"
ADMIN_ID = 123456789  # <-- ВСТАВЬ СВОЙ TELEGRAM ID

user_data_temp = {}

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Добро пожаловать в Караван Ми-Ерима.\n\n"
        "Для оформления заказа введите ваш НИК на сервере:"
    )
    context.user_data.clear()
    context.user_data["step"] = "nickname"

# ---------- TEXT HANDLER ----------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    step = context.user_data.get("step")

    # 1. Ник
    if step == "nickname":
        context.user_data["nickname"] = text
        context.user_data["step"] = "category"

        keyboard = [
            ["📦 Блоки", "⚔️ Предметы"],
            ["📚 Зачарования", "✍️ Другое"]
        ]

        await update.message.reply_text(
            "Выберите категорию товара:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # 2. Категория
    elif step == "category":
        context.user_data["category"] = text
        context.user_data["step"] = "item"

        await update.message.reply_text(
            "Введите название товара:",
            reply_markup=ReplyKeyboardRemove()
        )

    # 3. Товар
    elif step == "item":
        context.user_data["item"] = text
        context.user_data["step"] = "amount"

        await update.message.reply_text(
            "Введите количество (например: 3 стака, 2 шалкера, 1 шт):"
        )

    # 4. Количество
    elif step == "amount":
        context.user_data["amount"] = text
        context.user_data["step"] = "coords"

        await update.message.reply_text(
            "📍 Введите координаты доставки\n"
            "(в любом формате, как принято на сервере):"
        )

    # 5. Координаты
    elif step == "coords":
        context.user_data["coords"] = text
        context.user_data["step"] = "confirm"

        summary = (
            "📄 Проверьте заказ:\n\n"
            f"👤 Ник: {context.user_data['nickname']}\n"
            f"📦 Категория: {context.user_data['category']}\n"
            f"📦 Товар: {context.user_data['item']}\n"
            f"🔢 Количество: {context.user_data['amount']}\n"
            f"📍 Координаты: {context.user_data['coords']}\n\n"
            "Напишите:\n"
            "✅ Да — подтвердить\n"
            "❌ Нет — отменить"
        )

        await update.message.reply_text(summary)

    # 6. Подтверждение
    elif step == "confirm":
        if text.lower() in ["да", "yes", "y", "✅ да"]:
            order_text = (
                "📦 НОВЫЙ ЗАКАЗ\n\n"
                f"👤 Ник: {context.user_data['nickname']}\n"
                f"📦 Категория: {context.user_data['category']}\n"
                f"📦 Товар: {context.user_data['item']}\n"
                f"🔢 Количество: {context.user_data['amount']}\n"
                f"📍 Координаты: {context.user_data['coords']}"
            )

            await context.bot.send_message(chat_id=ADMIN_ID, text=order_text)

            await update.message.reply_text(
                "✅ Заказ принят.\n"
                "Караван Ми-Ерима уже готовится к отправке 🐪"
            )

            context.user_data.clear()

        else:
            await update.message.reply_text(
                "❌ Заказ отменён.\n"
                "Для нового заказа напишите /start"
            )
            context.user_data.clear()

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Бот запущен...")
    app.run_polling()

if name == "main":
    main()
