from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import ADMIN_IDS
from lang import t
import database as db

# Import states and helpers from handlers_user
from handlers_user import (
    MAIN_MENU, ADMIN_MENU, ADM_CREDIT_ID, ADM_CREDIT_AMT,
    ADM_BAN, ADM_UNBAN, ADM_BROADCAST,
    _edit_or_send, _delete_user_msg, main_menu_keyboard,
)


# ══════════════════════════════════════════════════════════════
#  Admin check decorator
# ══════════════════════════════════════════════════════════════

def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            if update.callback_query:
                await update.callback_query.answer(t("not_admin", "en"), show_alert=True)
            return  # None → ConversationHandler stays in current state
        return await func(update, context)
    return wrapper


async def get_admin_lang(user_id: int) -> str:
    user = await db.get_user(user_id)
    return user["lang"] if user else "en"


def admin_menu_keyboard(lang: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("btn_view_gmails", lang), callback_data="adm_gmails"),
            InlineKeyboardButton(t("btn_view_users", lang), callback_data="adm_users"),
        ],
        [
            InlineKeyboardButton(t("btn_add_credit", lang), callback_data="adm_add_credit"),
            InlineKeyboardButton(t("btn_withdrawals", lang), callback_data="adm_withdrawals"),
        ],
        [
            InlineKeyboardButton(t("btn_broadcast", lang), callback_data="adm_broadcast"),
        ],
        [
            InlineKeyboardButton(t("btn_ban_user", lang), callback_data="adm_ban"),
            InlineKeyboardButton(t("btn_unban_user", lang), callback_data="adm_unban"),
        ],
        [InlineKeyboardButton(t("btn_back", lang), callback_data="back_main")],
    ])


def admin_back_keyboard(lang: str):
    """Back button that returns to admin panel."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_back", lang), callback_data="admin_panel")]
    ])


# ══════════════════════════════════════════════════════════════
#  Admin Panel
# ══════════════════════════════════════════════════════════════

@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)

    user_count = await db.get_user_count()
    gmail_count = await db.get_gmail_count()
    pending = await db.get_pending_withdrawals()

    text = t("admin_panel", lang, users=user_count, gmails=gmail_count, pending=len(pending))
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=admin_menu_keyboard(lang))
    return ADMIN_MENU


# ══════════════════════════════════════════════════════════════
#  View Gmails
# ══════════════════════════════════════════════════════════════

@admin_only
async def view_gmails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)

    gmails = await db.get_all_gmails(limit=30)
    if not gmails:
        text = "📧 <b>No Gmails submitted yet.</b>"
    else:
        text = f"📧 <b>Recent Gmails</b> ({len(gmails)}):\n\n"
        for i, g in enumerate(gmails, 1):
            date = g["submitted_at"].strftime("%m/%d %H:%M")
            uname = f"@{g['username']}" if g.get('username') else g.get('full_name', '—')
            text += (
                f"<b>{i}.</b> <code>{g['email']}</code>\n"
                f"   🔑 <tg-spoiler>{g['password']}</tg-spoiler>\n"
                f"   👤 {uname} (<code>{g['telegram_id']}</code>) • {date}\n\n"
            )

    await query.edit_message_text(text, parse_mode="HTML", reply_markup=admin_back_keyboard(lang))
    return ADMIN_MENU


# ══════════════════════════════════════════════════════════════
#  View Users
# ══════════════════════════════════════════════════════════════

@admin_only
async def view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)

    users = await db.get_all_users()
    if not users:
        text = "👥 <b>No users yet.</b>"
    else:
        text = f"👥 <b>All Users</b> ({len(users)}):\n\n"
        for i, u in enumerate(users[:30], 1):
            status = "🚫" if u.get("is_banned") else "✅"
            lovable = f"🔑 {u.get('lovable_email', '—')}" if u.get("lovable_email") else "❌ No Lovable"
            text += (
                f"{status} <b>{i}.</b> {u['full_name']}\n"
                f"   🆔 <code>{u['telegram_id']}</code>\n"
                f"   💎 {u['balance']} pts | 📧 {u['gmails_submitted']} gmails\n"
                f"   {lovable}\n\n"
            )

    await query.edit_message_text(text, parse_mode="HTML", reply_markup=admin_back_keyboard(lang))
    return ADMIN_MENU


# ══════════════════════════════════════════════════════════════
#  Withdrawals
# ══════════════════════════════════════════════════════════════

@admin_only
async def view_withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)

    pending = await db.get_pending_withdrawals()
    if not pending:
        text = "🎁 <b>No pending withdrawal requests.</b>"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=admin_back_keyboard(lang))
        return ADMIN_MENU

    text = f"🎁 <b>Pending Withdrawals</b> ({len(pending)}):\n\n"
    for w in pending:
        user = await db.get_user(w["telegram_id"])
        name = user["full_name"] if user else "Unknown"
        lovable = user.get("lovable_email", "N/A") if user else "N/A"
        text += (
            f"👤 {name} (<code>{w['telegram_id']}</code>)\n"
            f"💎 {w['points']} pts\n"
            f"🔑 Lovable: <code>{lovable}</code>\n"
            f"🆔 WID: <code>{w['id']}</code>\n\n"
        )

    await query.edit_message_text(text, parse_mode="HTML", reply_markup=admin_back_keyboard(lang))
    return ADMIN_MENU


# ══════════════════════════════════════════════════════════════
#  Approve / Reject withdrawal  (inline from notification msgs)
# ══════════════════════════════════════════════════════════════

@admin_only
async def withdrawal_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles w_approve_<id> and w_reject_<id> from admin notification messages."""
    query = update.callback_query
    await query.answer()
    data = query.data

    parts = data.split("_", 2)
    action = parts[1]       # approve / reject
    w_id = parts[2]

    status = "approved" if action == "approve" else "rejected"
    await db.resolve_withdrawal(w_id, status)

    emoji = "✅" if status == "approved" else "❌"
    await query.edit_message_text(
        query.message.text_html + f"\n\n{emoji} <b>{status.upper()}</b>",
        parse_mode="HTML",
    )

    w = await db.get_withdrawal_by_id(w_id)
    if not w:
        return

    user = await db.get_user(w["telegram_id"])
    user_lang = user["lang"] if user else "en"
    lovable_email = user.get("lovable_email", "N/A") if user else "N/A"

    if status == "rejected":
        await db.refund_points(w["telegram_id"], w["points"])
        try:
            await context.bot.send_message(
                w["telegram_id"],
                t("notify_withdrawal_rejected", user_lang, points=w["points"]),
                parse_mode="HTML",
            )
        except Exception:
            pass

    if status == "approved":
        try:
            await context.bot.send_message(
                w["telegram_id"],
                t("notify_withdrawal_approved", user_lang, points=w["points"], lovable=lovable_email),
                parse_mode="HTML",
            )
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#  Add Credit
# ══════════════════════════════════════════════════════════════

@admin_only
async def add_credit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)
    await query.edit_message_text(
        t("add_credit_prompt_id", lang),
        parse_mode="HTML",
        reply_markup=admin_back_keyboard(lang),
    )
    return ADM_CREDIT_ID


async def add_credit_id_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: receive target user's Telegram ID."""
    if update.effective_user.id not in ADMIN_IDS:
        return ADMIN_MENU
    text_input = update.message.text.strip()
    await _delete_user_msg(update)
    lang = await get_admin_lang(update.effective_user.id)

    try:
        target_id = int(text_input)
    except ValueError:
        await _edit_or_send(
            update, context,
            "❌ Invalid ID. Send a numeric Telegram ID.",
            reply_markup=admin_back_keyboard(lang),
        )
        return ADM_CREDIT_ID

    target_user = await db.get_user(target_id)
    if not target_user:
        await _edit_or_send(
            update, context,
            t("user_not_found", lang),
            reply_markup=admin_back_keyboard(lang),
        )
        return ADM_CREDIT_ID

    context.user_data["add_credit_target"] = target_id
    lovable = target_user.get("lovable_email", "Not set")
    await _edit_or_send(
        update, context,
        t("add_credit_prompt_amount", lang,
          name=target_user["full_name"],
          tid=target_id,
          lovable=lovable),
        reply_markup=admin_back_keyboard(lang),
    )
    return ADM_CREDIT_AMT


async def add_credit_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: receive credit amount and process."""
    if update.effective_user.id not in ADMIN_IDS:
        return ADMIN_MENU
    text_input = update.message.text.strip()
    await _delete_user_msg(update)
    lang = await get_admin_lang(update.effective_user.id)

    try:
        amount = int(text_input)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await _edit_or_send(
            update, context,
            t("add_credit_invalid_amount", lang),
            reply_markup=admin_back_keyboard(lang),
        )
        return ADM_CREDIT_AMT

    target_id = context.user_data.get("add_credit_target")
    target_user = await db.get_user(target_id)
    if not target_user:
        await _edit_or_send(
            update, context,
            t("user_not_found", lang),
            reply_markup=admin_back_keyboard(lang),
        )
        return ADMIN_MENU

    # Record credit
    await db.add_admin_credit(target_id, amount, update.effective_user.id)

    # Notify user
    user_lang = target_user.get("lang", "en")
    lovable_email = target_user.get("lovable_email", "N/A")
    try:
        await context.bot.send_message(
            target_id,
            t("notify_credit_added", user_lang, amount=amount, lovable=lovable_email),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # Show confirmation + admin panel
    user_count = await db.get_user_count()
    gmail_count = await db.get_gmail_count()
    pending = await db.get_pending_withdrawals()

    text = (
        t("add_credit_done", lang, amount=amount, name=target_user["full_name"])
        + "\n\n"
        + t("admin_panel", lang, users=user_count, gmails=gmail_count, pending=len(pending))
    )
    await _edit_or_send(update, context, text, reply_markup=admin_menu_keyboard(lang))
    return ADMIN_MENU


# ══════════════════════════════════════════════════════════════
#  Broadcast
# ══════════════════════════════════════════════════════════════

@admin_only
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)
    await query.edit_message_text(
        t("broadcast_prompt", lang),
        parse_mode="HTML",
        reply_markup=admin_back_keyboard(lang),
    )
    return ADM_BROADCAST


async def broadcast_msg_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive broadcast message and send to all users."""
    if update.effective_user.id not in ADMIN_IDS:
        return ADMIN_MENU
    msg_text = update.message.text
    await _delete_user_msg(update)
    lang = await get_admin_lang(update.effective_user.id)

    users = await db.get_all_users()
    sent = 0
    for u in users:
        try:
            await context.bot.send_message(u["telegram_id"], msg_text, parse_mode="HTML")
            sent += 1
        except Exception:
            pass

    # Show result + admin panel
    user_count = await db.get_user_count()
    gmail_count = await db.get_gmail_count()
    pending = await db.get_pending_withdrawals()

    text = (
        t("broadcast_done", lang, count=sent)
        + "\n\n"
        + t("admin_panel", lang, users=user_count, gmails=gmail_count, pending=len(pending))
    )
    await _edit_or_send(update, context, text, reply_markup=admin_menu_keyboard(lang))
    return ADMIN_MENU


# ══════════════════════════════════════════════════════════════
#  Ban / Unban
# ══════════════════════════════════════════════════════════════

@admin_only
async def ban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)
    await query.edit_message_text(
        t("ban_prompt", lang),
        parse_mode="HTML",
        reply_markup=admin_back_keyboard(lang),
    )
    return ADM_BAN


@admin_only
async def unban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)
    await query.edit_message_text(
        t("unban_prompt", lang),
        parse_mode="HTML",
        reply_markup=admin_back_keyboard(lang),
    )
    return ADM_UNBAN


async def ban_id_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive user ID and ban them."""
    if update.effective_user.id not in ADMIN_IDS:
        return ADMIN_MENU
    text_input = update.message.text.strip()
    await _delete_user_msg(update)
    lang = await get_admin_lang(update.effective_user.id)

    try:
        target_id = int(text_input)
    except ValueError:
        await _edit_or_send(
            update, context,
            "❌ Invalid ID. Send a numeric Telegram ID.",
            reply_markup=admin_back_keyboard(lang),
        )
        return ADM_BAN

    target_user = await db.get_user(target_id)
    if not target_user:
        await _edit_or_send(
            update, context,
            t("user_not_found", lang),
            reply_markup=admin_back_keyboard(lang),
        )
        return ADM_BAN

    await db.ban_user(target_id, True)

    # Show result + admin panel
    user_count = await db.get_user_count()
    gmail_count = await db.get_gmail_count()
    pending = await db.get_pending_withdrawals()

    text = (
        t("ban_done", lang, tid=target_id)
        + "\n\n"
        + t("admin_panel", lang, users=user_count, gmails=gmail_count, pending=len(pending))
    )
    await _edit_or_send(update, context, text, reply_markup=admin_menu_keyboard(lang))
    return ADMIN_MENU


async def unban_id_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive user ID and unban them."""
    if update.effective_user.id not in ADMIN_IDS:
        return ADMIN_MENU
    text_input = update.message.text.strip()
    await _delete_user_msg(update)
    lang = await get_admin_lang(update.effective_user.id)

    try:
        target_id = int(text_input)
    except ValueError:
        await _edit_or_send(
            update, context,
            "❌ Invalid ID. Send a numeric Telegram ID.",
            reply_markup=admin_back_keyboard(lang),
        )
        return ADM_UNBAN

    target_user = await db.get_user(target_id)
    if not target_user:
        await _edit_or_send(
            update, context,
            t("user_not_found", lang),
            reply_markup=admin_back_keyboard(lang),
        )
        return ADM_UNBAN

    await db.ban_user(target_id, False)

    # Show result + admin panel
    user_count = await db.get_user_count()
    gmail_count = await db.get_gmail_count()
    pending = await db.get_pending_withdrawals()

    text = (
        t("unban_done", lang, tid=target_id)
        + "\n\n"
        + t("admin_panel", lang, users=user_count, gmails=gmail_count, pending=len(pending))
    )
    await _edit_or_send(update, context, text, reply_markup=admin_menu_keyboard(lang))
    return ADMIN_MENU


# ══════════════════════════════════════════════════════════════
#  Register withdrawal handler  (outside conversation)
# ══════════════════════════════════════════════════════════════

def register_admin_handlers(app):
    """Register the withdrawal approve/reject handler.
    This runs on admin notification messages, not in the conversation.
    """
    app.add_handler(CallbackQueryHandler(withdrawal_action, pattern=r"^w_(approve|reject)_"))
