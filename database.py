from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_col = db["users"]
gmails_col = db["gmails"]
withdrawals_col = db["withdrawals"]


# ══════════════════════════════════════════════════════════════
#  USER operations
# ══════════════════════════════════════════════════════════════

async def get_user(telegram_id: int) -> dict | None:
    return await users_col.find_one({"telegram_id": telegram_id})


async def create_user(telegram_id: int, full_name: str, username: str | None, lang: str = "en") -> dict:
    doc = {
        "telegram_id": telegram_id,
        "full_name": full_name,
        "username": username,
        "lang": lang,
        "lovable_email": None,
        "lovable_password": None,
        "balance": 0,
        "total_earned": 0,
        "gmails_submitted": 0,
        "is_banned": False,
        "created_at": datetime.now(timezone.utc),
    }
    await users_col.insert_one(doc)
    return doc


async def set_user_lang(telegram_id: int, lang: str):
    await users_col.update_one({"telegram_id": telegram_id}, {"$set": {"lang": lang}})


async def set_lovable_account(telegram_id: int, email: str, password: str):
    await users_col.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"lovable_email": email, "lovable_password": password}},
    )


async def add_points(telegram_id: int, points: int):
    await users_col.update_one(
        {"telegram_id": telegram_id},
        {"$inc": {"balance": points, "total_earned": points, "gmails_submitted": 1}},
    )


async def deduct_points(telegram_id: int, points: int):
    await users_col.update_one(
        {"telegram_id": telegram_id},
        {"$inc": {"balance": -points}},
    )


async def ban_user(telegram_id: int, ban: bool = True):
    await users_col.update_one({"telegram_id": telegram_id}, {"$set": {"is_banned": ban}})


async def get_all_users():
    return await users_col.find().to_list(length=None)


async def get_user_count() -> int:
    return await users_col.count_documents({})


# ══════════════════════════════════════════════════════════════
#  GMAIL operations
# ══════════════════════════════════════════════════════════════

async def gmail_exists(email: str) -> bool:
    return await gmails_col.find_one({"email": email.lower()}) is not None


async def add_gmail(telegram_id: int, email: str, password: str, points_awarded: int) -> dict:
    doc = {
        "telegram_id": telegram_id,
        "email": email.lower(),
        "password": password,
        "points_awarded": points_awarded,
        "submitted_at": datetime.now(timezone.utc),
    }
    await gmails_col.insert_one(doc)
    return doc


async def get_user_gmails(telegram_id: int) -> list:
    return await gmails_col.find({"telegram_id": telegram_id}).sort("submitted_at", -1).to_list(length=None)


async def get_gmail_count() -> int:
    return await gmails_col.count_documents({})


async def get_all_gmails(limit: int = 50):
    return await gmails_col.find().sort("submitted_at", -1).to_list(length=limit)


# ══════════════════════════════════════════════════════════════
#  WITHDRAWAL operations
# ══════════════════════════════════════════════════════════════

async def create_withdrawal(telegram_id: int, points: int):
    doc = {
        "telegram_id": telegram_id,
        "points": points,
        "status": "pending",          # pending / approved / rejected
        "created_at": datetime.now(timezone.utc),
        "resolved_at": None,
    }
    result = await withdrawals_col.insert_one(doc)
    return str(result.inserted_id)


async def get_pending_withdrawals():
    return await withdrawals_col.find({"status": "pending"}).to_list(length=None)


async def resolve_withdrawal(withdrawal_id, status: str):
    from bson import ObjectId
    await withdrawals_col.update_one(
        {"_id": ObjectId(withdrawal_id)},
        {"$set": {"status": status, "resolved_at": datetime.now(timezone.utc)}},
    )


# ══════════════════════════════════════════════════════════════
#  ADMIN CREDIT operations
# ══════════════════════════════════════════════════════════════

credits_col = db["admin_credits"]

async def add_admin_credit(telegram_id: int, amount: int, admin_id: int) -> dict:
    """Record admin manually adding Lovable credits to a user."""
    doc = {
        "telegram_id": telegram_id,
        "amount": amount,
        "added_by_admin": admin_id,
        "created_at": datetime.now(timezone.utc),
    }
    await credits_col.insert_one(doc)
    # Deduct from user's points balance (they "spent" their points)
    await users_col.update_one(
        {"telegram_id": telegram_id},
        {"$inc": {"total_credits_received": amount}},
    )
    return doc


async def get_user_credits(telegram_id: int) -> list:
    return await credits_col.find({"telegram_id": telegram_id}).sort("created_at", -1).to_list(length=None)
