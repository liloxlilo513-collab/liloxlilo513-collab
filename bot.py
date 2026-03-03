import logging
import asyncio
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from database import init_db
from handlers_user import build_user_conversation
from handlers_admin import register_admin_handlers

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s │ %(name)s │ %(levelname)s │ %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set! Add it to .env file.")
        return

    # ── Connect to PostgreSQL and create tables ──
    logger.info("🔗  Connecting to PostgreSQL...")
    await init_db()
    logger.info("✅  Database ready.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Single ConversationHandler for ALL user + admin flows
    app.add_handler(build_user_conversation())

    # Withdrawal approve/reject (works on admin notification messages)
    register_admin_handlers(app)

    logger.info("🤖  Bot is starting...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    # Keep running until stopped
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
