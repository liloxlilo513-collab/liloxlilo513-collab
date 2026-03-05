import asyncpg
import ssl
from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE, PG_SSL

# ── Connection pool (initialized on bot startup) ──────────────
_pool: asyncpg.Pool | None = None


async def init_db():
    """Create connection pool and ensure all tables exist."""
    global _pool

    ssl_ctx = None
    if PG_SSL == "require":
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

    _pool = await asyncpg.create_pool(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DATABASE,
        ssl=ssl_ctx,
        min_size=1,
        max_size=10,
    )
    await _create_tables()


async def _create_tables():
    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id            BIGINT PRIMARY KEY,
                full_name              TEXT        NOT NULL,
                username               TEXT,
                lang                   TEXT        NOT NULL DEFAULT 'en',
                lovable_email          TEXT,
                lovable_password       TEXT,
                balance                INT         NOT NULL DEFAULT 0,
                total_earned           INT         NOT NULL DEFAULT 0,
                total_credits_received INT         NOT NULL DEFAULT 0,
                gmails_submitted       INT         NOT NULL DEFAULT 0,
                is_banned              BOOLEAN     NOT NULL DEFAULT FALSE,
                created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS gmails (
                id             SERIAL PRIMARY KEY,
                telegram_id    BIGINT      NOT NULL,
                email          TEXT        NOT NULL UNIQUE,
                password       TEXT        NOT NULL,
                points_awarded INT         NOT NULL,
                submitted_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS withdrawals (
                id          SERIAL PRIMARY KEY,
                telegram_id BIGINT      NOT NULL,
                points      INT         NOT NULL,
                status      TEXT        NOT NULL DEFAULT 'pending',
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                resolved_at TIMESTAMPTZ
            );
            CREATE TABLE IF NOT EXISTS admin_credits (
                id             SERIAL PRIMARY KEY,
                telegram_id    BIGINT      NOT NULL,
                amount         INT         NOT NULL,
                added_by_admin BIGINT      NOT NULL,
                created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)


def _pool_check():
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db() first.")
    return _pool


# ══════════════════════════════════════════════════════════════
#  USER operations
# ══════════════════════════════════════════════════════════════

async def get_user(telegram_id: int) -> dict | None:
    async with _pool_check().acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        return dict(row) if row else None


async def create_user(telegram_id: int, full_name: str, username: str | None, lang: str = "en") -> dict:
    async with _pool_check().acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO users (telegram_id, full_name, username, lang)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) DO NOTHING
            RETURNING *
            """,
            telegram_id, full_name, username, lang,
        )
        if row:
            return dict(row)
        return await get_user(telegram_id)


async def set_user_lang(telegram_id: int, lang: str):
    async with _pool_check().acquire() as conn:
        await conn.execute(
            "UPDATE users SET lang = $1 WHERE telegram_id = $2", lang, telegram_id
        )


async def set_lovable_account(telegram_id: int, email: str, password: str):
    async with _pool_check().acquire() as conn:
        await conn.execute(
            "UPDATE users SET lovable_email = $1, lovable_password = $2 WHERE telegram_id = $3",
            email, password, telegram_id,
        )


async def add_points(telegram_id: int, points: int):
    async with _pool_check().acquire() as conn:
        await conn.execute(
            """
            UPDATE users
            SET balance = balance + $1,
                total_earned = total_earned + $1,
                gmails_submitted = gmails_submitted + 1
            WHERE telegram_id = $2
            """,
            points, telegram_id,
        )


async def deduct_points(telegram_id: int, points: int):
    async with _pool_check().acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = balance - $1 WHERE telegram_id = $2",
            points, telegram_id,
        )


async def refund_points(telegram_id: int, points: int):
    """Add points back to balance only (used for rejected withdrawals)."""
    async with _pool_check().acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = balance + $1 WHERE telegram_id = $2",
            points, telegram_id,
        )


async def ban_user(telegram_id: int, ban: bool = True):
    async with _pool_check().acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_banned = $1 WHERE telegram_id = $2", ban, telegram_id
        )


async def get_all_users() -> list:
    async with _pool_check().acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(r) for r in rows]


async def get_user_count() -> int:
    async with _pool_check().acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM users")


# ══════════════════════════════════════════════════════════════
#  GMAIL operations
# ══════════════════════════════════════════════════════════════

async def gmail_exists(email: str) -> bool:
    async with _pool_check().acquire() as conn:
        val = await conn.fetchval("SELECT 1 FROM gmails WHERE email = $1", email.lower())
        return val is not None


async def add_gmail(telegram_id: int, email: str, password: str, points_awarded: int) -> dict:
    async with _pool_check().acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO gmails (telegram_id, email, password, points_awarded)
            VALUES ($1, $2, $3, $4) RETURNING *
            """,
            telegram_id, email.lower(), password, points_awarded,
        )
        return dict(row)


async def get_user_gmails(telegram_id: int) -> list:
    async with _pool_check().acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM gmails WHERE telegram_id = $1 ORDER BY submitted_at DESC",
            telegram_id,
        )
        return [dict(r) for r in rows]


async def get_gmail_count() -> int:
    async with _pool_check().acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM gmails")


async def get_all_gmails(limit: int = 50) -> list:
    async with _pool_check().acquire() as conn:
        rows = await conn.fetch(
            "SELECT g.*, u.username, u.full_name "
            "FROM gmails g LEFT JOIN users u ON g.telegram_id = u.telegram_id "
            "ORDER BY g.submitted_at DESC LIMIT $1", limit
        )
        return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════
#  WITHDRAWAL operations
# ══════════════════════════════════════════════════════════════

async def create_withdrawal(telegram_id: int, points: int) -> int:
    async with _pool_check().acquire() as conn:
        w_id = await conn.fetchval(
            "INSERT INTO withdrawals (telegram_id, points) VALUES ($1, $2) RETURNING id",
            telegram_id, points,
        )
        return w_id


async def get_pending_withdrawals() -> list:
    async with _pool_check().acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM withdrawals WHERE status = 'pending' ORDER BY created_at"
        )
        return [dict(r) for r in rows]


async def resolve_withdrawal(withdrawal_id, status: str):
    async with _pool_check().acquire() as conn:
        await conn.execute(
            "UPDATE withdrawals SET status = $1, resolved_at = NOW() WHERE id = $2",
            status, int(withdrawal_id),
        )


async def get_withdrawal_by_id(withdrawal_id) -> dict | None:
    async with _pool_check().acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM withdrawals WHERE id = $1", int(withdrawal_id)
        )
        return dict(row) if row else None


# ══════════════════════════════════════════════════════════════
#  ADMIN CREDIT operations
# ══════════════════════════════════════════════════════════════

async def add_admin_credit(telegram_id: int, amount: int, admin_id: int) -> dict:
    """Record admin manually adding Lovable credits to a user."""
    async with _pool_check().acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO admin_credits (telegram_id, amount, added_by_admin)
            VALUES ($1, $2, $3) RETURNING *
            """,
            telegram_id, amount, admin_id,
        )
        await conn.execute(
            "UPDATE users SET total_credits_received = total_credits_received + $1 WHERE telegram_id = $2",
            amount, telegram_id,
        )
        return dict(row)


async def get_user_credits(telegram_id: int) -> list:
    async with _pool_check().acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM admin_credits WHERE telegram_id = $1 ORDER BY created_at DESC",
            telegram_id,
        )
        return [dict(r) for r in rows]
