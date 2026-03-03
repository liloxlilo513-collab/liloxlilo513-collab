from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from config import ADMIN_IDS
from lang import t
import database as db


# ══════════════════════════════════════════════════════════════
#  Admin check decorator
# ══════════════════════════════════════════════════════════════

def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            if update.callback_query:
                await update.callback_query.answer(t("not_admin", "en"), show_alert=True)
            return
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
            text += (
                f"<b>{i}.</b> <code>{g['email']}</code>\n"
                f"   🔑 <tg-spoiler>{g['password']}</tg-spoiler>\n"
                f"   👤 <code>{g['telegram_id']}</code> • {date}\n\n"
            )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_back", lang), callback_data="admin_panel")]
    ])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)


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

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_back", lang), callback_data="admin_panel")]
    ])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)


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
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_back", lang), callback_data="admin_panel")]
        ])
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
        return

    text = f"🎁 <b>Pending Withdrawals</b> ({len(pending)}):\n\n"
    for w in pending:
        user = await db.get_user(w["telegram_id"])
        name = user["full_name"] if user else "Unknown"
        lovable = user.get("lovable_email", "N/A") if user else "N/A"
        text += (
            f"👤 {name} (<code>{w['telegram_id']}</code>)\n"
            f"💎 {w['points']} pts\n"
            f"🔑 Lovable: <code>{lovable}</code>\n"
            f"🆔 WID: <code>{w['_id']}</code>\n\n"
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_back", lang), callback_data="admin_panel")]
    ])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)


# ══════════════════════════════════════════════════════════════
#  Approve / Reject withdrawal (inline from notification)
# ══════════════════════════════════════════════════════════════

@admin_only
async def withdrawal_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # w_approve_<id> or w_reject_<id>

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

    from bson import ObjectId
    w = await db.withdrawals_col.find_one({"_id": ObjectId(w_id)})
    if not w:
        return

    user = await db.get_user(w["telegram_id"])
    user_lang = user["lang"] if user else "en"
    lovable_email = user.get("lovable_email", "N/A") if user else "N/A"

    if status == "rejected":
        # Refund points
        await db.users_col.update_one(
            {"telegram_id": w["telegram_id"]},
            {"$inc": {"balance": w["points"]}},
        )
        # Beautiful rejection notification
        try:
            await context.bot.send_message(
                w["telegram_id"],
                t("notify_withdrawal_rejected", user_lang, points=w["points"]),
                parse_mode="HTML",
            )
        except Exception:
            pass

    if status == "approved":
        # Beautiful approval notification
        try:
            await context.bot.send_message(
                w["telegram_id"],
                t("notify_withdrawal_approved", user_lang, points=w["points"], lovable=lovable_email),
                parse_mode="HTML",
            )
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#  Add Credit to User (Admin manually adds Lovable credits)
# ══════════════════════════════════════════════════════════════

@admin_only
async def add_credit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)
    context.user_data["admin_action"] = "add_credit_id"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_cancel", lang), callback_data="admin_panel")]
    ])
    await query.edit_message_text(
        t("add_credit_prompt_id", lang),
        parse_mode="HTML",
        reply_markup=kb,
    )


async def add_credit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the multi-step add credit flow for admin."""
    action = context.user_data.get("admin_action")
    if action not in ("add_credit_id", "add_credit_amount"):
        return
    if update.effective_user.id not in ADMIN_IDS:
        return

    lang = await get_admin_lang(update.effective_user.id)

    if action == "add_credit_id":
        # Step 1: receive telegram ID
        try:
            target_id = int(update.message.text.strip())
        except ValueError:
            await update.message.reply_text("❌ Invalid ID. Send a numeric Telegram ID.")
            return

        target_user = await db.get_user(target_id)
        if not target_user:
            await update.message.reply_text(t("user_not_found", lang), parse_mode="HTML")
            return

        context.user_data["add_credit_target"] = target_id
        context.user_data["admin_action"] = "add_credit_amount"

        lovable = target_user.get("lovable_email", "Not set")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_cancel", lang), callback_data="admin_panel")]
        ])
        await update.message.reply_text(
            t("add_credit_prompt_amount", lang,
              name=target_user["full_name"],
              tid=target_id,
              lovable=lovable),
            parse_mode="HTML",
            reply_markup=kb,
        )

    elif action == "add_credit_amount":
        # Step 2: receive credit amount
        try:
            amount = int(update.message.text.strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text(t("add_credit_invalid_amount", lang), parse_mode="HTML")
            return

        target_id = context.user_data.get("add_credit_target")
        context.user_data.pop("admin_action", None)
        context.user_data.pop("add_credit_target", None)

        target_user = await db.get_user(target_id)
        if not target_user:
            await update.message.reply_text(t("user_not_found", lang), parse_mode="HTML")
            return

        # Record the credit addition in DB
        await db.add_admin_credit(target_id, amount, update.effective_user.id)

        user_lang = target_user.get("lang", "en")
        lovable_email = target_user.get("lovable_email", "N/A")

        # Send beautiful notification to user
        try:
            await context.bot.send_message(
                target_id,
                t("notify_credit_added", user_lang, amount=amount, lovable=lovable_email),
                parse_mode="HTML",
            )
        except Exception:
            pass

        # Confirm to admin
        from handlers_user import main_menu_keyboard
        await update.message.reply_text(
            t("add_credit_done", lang, amount=amount, name=target_user["full_name"]),
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(lang, True),
        )


# ══════════════════════════════════════════════════════════════
#  Broadcast
# ══════════════════════════════════════════════════════════════

@admin_only
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)
    context.user_data["admin_action"] = "broadcast"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_cancel", lang), callback_data="admin_panel")]
    ])
    await query.edit_message_text(t("broadcast_prompt", lang), parse_mode="HTML", reply_markup=kb)


@admin_only
async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("admin_action") != "broadcast":
        return
    context.user_data.pop("admin_action", None)
    lang = await get_admin_lang(update.effective_user.id)

    msg = update.message.text
    users = await db.get_all_users()
    sent = 0
    for u in users:
        try:
            await context.bot.send_message(u["telegram_id"], msg, parse_mode="HTML")
            sent += 1
        except Exception:
            pass

    from handlers_user import main_menu_keyboard
    await update.message.reply_text(
        t("broadcast_done", lang, count=sent),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang, True),
    )


# ══════════════════════════════════════════════════════════════
#  Ban / Unban
# ══════════════════════════════════════════════════════════════

@admin_only
async def ban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)
    context.user_data["admin_action"] = "ban"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_cancel", lang), callback_data="admin_panel")]
    ])
    await query.edit_message_text(t("ban_prompt", lang), parse_mode="HTML", reply_markup=kb)


@admin_only
async def unban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_admin_lang(update.effective_user.id)
    context.user_data["admin_action"] = "unban"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_cancel", lang), callback_data="admin_panel")]
    ])
    await query.edit_message_text(t("unban_prompt", lang), parse_mode="HTML", reply_markup=kb)


async def ban_unban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ban/unban text input from admin."""
    action = context.user_data.get("admin_action")
    if action not in ("ban", "unban"):
        return
    if update.effective_user.id not in ADMIN_IDS:
        return

    context.user_data.pop("admin_action", None)
    lang = await get_admin_lang(update.effective_user.id)

    try:
        target_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Invalid ID. Send a numeric Telegram ID.")
        return

    target_user = await db.get_user(target_id)
    if not target_user:
        await update.message.reply_text(t("user_not_found", lang), parse_mode="HTML")
        return

    if action == "ban":
        await db.ban_user(target_id, True)
        text = t("ban_done", lang, tid=target_id)
    else:
        await db.ban_user(target_id, False)
        text = t("unban_done", lang, tid=target_id)

    from handlers_user import main_menu_keyboard
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_keyboard(lang, True))


# ══════════════════════════════════════════════════════════════
#  Register admin handlers
# ══════════════════════════════════════════════════════════════

def register_admin_handlers(app):
    """Register all admin callback query handlers."""
    app.add_handler(CallbackQueryHandler(admin_panel, pattern=r"^admin_panel$"))
    app.add_handler(CallbackQueryHandler(view_gmails, pattern=r"^adm_gmails$"))
    app.add_handler(CallbackQueryHandler(view_users, pattern=r"^adm_users$"))
    app.add_handler(CallbackQueryHandler(view_withdrawals, pattern=r"^adm_withdrawals$"))
    app.add_handler(CallbackQueryHandler(add_credit_start, pattern=r"^adm_add_credit$"))
    app.add_handler(CallbackQueryHandler(broadcast_start, pattern=r"^adm_broadcast$"))
    app.add_handler(CallbackQueryHandler(ban_start, pattern=r"^adm_ban$"))
    app.add_handler(CallbackQueryHandler(unban_start, pattern=r"^adm_unban$"))
    app.add_handler(CallbackQueryHandler(withdrawal_action, pattern=r"^w_(approve|reject)_"))
    # Text handlers for admin actions (add credit / broadcast / ban / unban)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_credit_handler), group=1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ban_unban_handler), group=2)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_send), group=3)
