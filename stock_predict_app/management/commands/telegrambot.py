import os
import django
from telegram import Update
from django.core.management.base import BaseCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_predict.settings')
django.setup()

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

from stock_predict_app.models import TelegramUser, Prediction, User
from stock_predict_app.utils import predict_stock_price


@sync_to_async
def link_telegram_user(chat_id, username):
    try:
        user = User.objects.get(username=username)
        TelegramUser.objects.get_or_create(user=user, chat_id=chat_id)
        return True, f"Telegram successfully linked to account '{username}'."
    except User.DoesNotExist:
        return False, f"No account found with username '{username}'. Please make sure you typed it correctly."


@sync_to_async
def get_user_by_chat_id(chat_id):
    try:
        return TelegramUser.objects.get(chat_id=chat_id).user
    except TelegramUser.DoesNotExist:
        return None


@sync_to_async
def get_latest_prediction(user):
    return Prediction.objects.filter(user=user).order_by("-created_at").first()

@sync_to_async
def is_user_pro(user):
    return user.userprofile.is_pro

@sync_to_async
def get_daily_prediction_count(user, date):
    return Prediction.objects.filter(user=user, created_at__date=date).count()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "Usage:\n/start your_site_username\n\nMake sure this matches the username you used to register on the site."
        )
        return

    username = args[0]
    success, message = await link_telegram_user(chat_id, username)

    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Link Telegram to your account\n"
        "/predict <TICKER> - Predict next-day price\n"
        "/latest - Show your most recent prediction\n"
        "/subscribe - Upgrade subscription to enjoy unlimited predictions\n"
        "/help - Show this help message"
    )


async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = await get_user_by_chat_id(chat_id)
    print(user.username)

    if not user:
        await update.message.reply_text("You need to link your account first using /start.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /predict <TICKER>")
        return
    
    if not await is_user_pro(user):
        today = timezone.now().date()
        count = await get_daily_prediction_count(user, today)
        if count >= 5:
            await update.message.reply_text(
                "⛔ Free users can only make 5 predictions per day.\nUpgrade to Pro: /subscribe"
            )
            return

    ticker = context.args[0].upper()
    try:
        prediction = await sync_to_async(predict_stock_price)(ticker)
        msg = f"{ticker} Prediction:\nPrice: {prediction.predicted_price}\nMSE: {prediction.mse}\nRMSE: {prediction.rmse}\nR²: {prediction.r2}"
        await update.message.reply_text(msg)
        await context.bot.send_photo(chat_id=chat_id, photo=open(prediction.plot_history.path, 'rb'))
        await context.bot.send_photo(chat_id=chat_id, photo=open(prediction.plot_comparison.path, 'rb'))
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user:
        await update.message.reply_text("You need to link your account first using /start.")
        return

    prediction = await get_latest_prediction(user)
    if not prediction:
        await update.message.reply_text("No predictions found.")
        return

    msg = f"Latest prediction:\n{prediction.ticker}\nPrice: {prediction.predicted_price}\nMSE: {prediction.mse}\nRMSE: {prediction.rmse}\nR²: {prediction.r2}"
    await update.message.reply_text(msg)
    await context.bot.send_photo(chat_id=chat_id, photo=open(prediction.plot_history.path, 'rb'))
    await context.bot.send_photo(chat_id=chat_id, photo=open(prediction.plot_comparism.path, 'rb'))

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user:
        await update.message.reply_text("Link your account first using /start.")
        return

    base_url = os.getenv("SITE_URL")

    subscribe_url = f"{base_url}/api/subscribe/"

    await update.message.reply_text(
        f"🛒 To upgrade to Pro and get unlimited predictions, click below:\n\n{subscribe_url}"
    )


class Command(BaseCommand):
    help = "Run Telegram bot with long polling"

    def handle(self, *args, **kwargs):
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("predict", predict))
        app.add_handler(CommandHandler("latest", latest))
        app.add_handler(CommandHandler("subscribe", subscribe))
        self.stdout.write("Telegram bot running...")
        app.run_polling()