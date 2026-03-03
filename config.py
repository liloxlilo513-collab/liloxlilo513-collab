import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram Bot ──────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# ── PostgreSQL (DigitalOcean) ─────────────────────────────────
PG_HOST     = os.getenv("PG_HOST", "localhost")
PG_PORT     = int(os.getenv("PG_PORT", "5432"))
PG_USER     = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")
PG_DATABASE = os.getenv("PG_DATABASE", "defaultdb")
PG_SSL      = os.getenv("PG_SSL", "require")   # require / disable

# ── Points ────────────────────────────────────────────────────
POINTS_PER_GMAIL = int(os.getenv("POINTS_PER_GMAIL", "100"))

# ── Bot Info ──────────────────────────────────────────────────
BOT_NAME = os.getenv("BOT_NAME", "Lovable Credits Bot")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@support")
