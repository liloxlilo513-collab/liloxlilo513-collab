import logging
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers_user import build_user_conversation
from handlers_admin import register_admin_handlers

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s │ %(name)s │ %(levelname)s │ %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set! Add it to .env file.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register user conversation (handles /start and all user flows)
    app.add_handler(build_user_conversation())

    # Register admin handlers (panels, add credit, broadcast, ban, etc.)
    register_admin_handlers(app)

    logger.info("🤖  Bot is starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
