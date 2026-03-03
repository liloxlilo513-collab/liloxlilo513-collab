import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram Bot ──────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# ── MongoDB ───────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "lovable_credits_bot")

# ── Points ────────────────────────────────────────────────────
POINTS_PER_GMAIL = int(os.getenv("POINTS_PER_GMAIL", "100"))

# ── Bot Info ──────────────────────────────────────────────────
BOT_NAME = os.getenv("BOT_NAME", "Lovable Credits Bot")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@support")
