import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from config import POINTS_PER_GMAIL, SUPPORT_USERNAME, ADMIN_IDS
from lang import t
import database as db

# ── Conversation states (user + admin in one handler) ─────────
(
    CHOOSE_LANG,
    MAIN_MENU,
    LOVABLE_EMAIL,
    LOVABLE_PASS,
    GMAIL_EMAIL,
    GMAIL_PASS,
    WITHDRAW_CONFIRM,
    ADMIN_MENU,
    ADM_CREDIT_ID,
    ADM_CREDIT_AMT,
    ADM_BAN,
    ADM_UNBAN,
    ADM_BROADCAST,
) = range(13)

GMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", re.IGNORECASE)


# ══════════════════════════════════════════════════════════════
#  Helpers – single-message editing  (no more stacking!)
# ══════════════════════════════════════════════════════════════

async def _edit_or_send(update, context, text, reply_markup=None):
    """Edit the tracked bot message. Falls back to sending a new one."""
    chat_id = update.effective_chat.id
    msg_id = context.user_data.get("bot_msg_id")
    try:
        if msg_id:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            return
    except Exception:
        pass
    # Fallback: send new message and track it
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    context.user_data["bot_msg_id"] = msg.message_id


async def _delete_user_msg(update):
    """Silently delete the user's typed message to keep the chat clean."""
    try:
        await update.message.delete()
    except Exception:
        pass


async def get_lang(user_id: int) -> str:
    user = await db.get_user(user_id)
    return user["lang"] if user else "en"


def main_menu_keyboard(lang: str, is_admin: bool = False):
    kb = [
        [InlineKeyboardButton(t("btn_submit_gmail", lang), callback_data="submit_gmail")],
        [
            InlineKeyboardButton(t("btn_my_account", lang), callback_data="my_account"),
            InlineKeyboardButton(t("btn_balance", lang), callback_data="balance"),
        ],
        [
            InlineKeyboardButton(t("btn_history", lang), callback_data="history"),
            InlineKeyboardButton(t("btn_set_lovable", lang), callback_data="set_lovable"),
        ],
        [
            InlineKeyboardButton(t("btn_withdraw", lang), callback_data="withdraw"),
            InlineKeyboardButton(t("btn_language", lang), callback_data="change_lang"),
        ],
        [InlineKeyboardButton(t("btn_support", lang), url=f"https://t.me/{SUPPORT_USERNAME.lstrip('@')}")],
    ]
    if is_admin:
        kb.append([InlineKeyboardButton(t("btn_admin_panel", lang), callback_data="admin_panel")])
    return InlineKeyboardMarkup(kb)


def cancel_keyboard(lang: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel")]
    ])


def back_keyboard(lang: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_back", lang), callback_data="back_main")]
    ])


# ══════════════════════════════════════════════════════════════
#  /start — entry point
# ══════════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Delete the /start command to keep chat clean
    await _delete_user_msg(update)

    db_user = await db.get_user(user.id)

    if not db_user:
        # New user → language picker
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
                InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
            ]
        ])
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("welcome", "en"),
            parse_mode="HTML",
            reply_markup=kb,
        )
        context.user_data["bot_msg_id"] = msg.message_id
        return CHOOSE_LANG

    if db_user.get("is_banned"):
        lang = db_user["lang"]
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("banned", lang),
            parse_mode="HTML",
        )
        context.user_data["bot_msg_id"] = msg.message_id
        return ConversationHandler.END

    lang = db_user["lang"]
    is_admin = user.id in ADMIN_IDS
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=t("main_menu", lang),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang, is_admin),
    )
    context.user_data["bot_msg_id"] = msg.message_id
    return MAIN_MENU


# ══════════════════════════════════════════════════════════════
#  Language selection
# ══════════════════════════════════════════════════════════════

async def language_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = "ar" if query.data == "lang_ar" else "en"
    user = update.effective_user

    db_user = await db.get_user(user.id)
    if not db_user:
        await db.create_user(user.id, user.full_name, user.username, lang)
    else:
        await db.set_user_lang(user.id, lang)

    is_admin = user.id in ADMIN_IDS
    await query.edit_message_text(
        t("lang_set", lang) + "\n\n" + t("main_menu", lang),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang, is_admin),
    )
    return MAIN_MENU


async def change_lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_lang(update.effective_user.id)
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
        ],
        [InlineKeyboardButton(t("btn_back", lang), callback_data="back_main")],
    ])
    await query.edit_message_text(t("choose_lang", lang), parse_mode="HTML", reply_markup=kb)
    return CHOOSE_LANG


# ══════════════════════════════════════════════════════════════
#  Back to main / Cancel
# ══════════════════════════════════════════════════════════════

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    lang = await get_lang(user.id)
    is_admin = user.id in ADMIN_IDS
    await query.edit_message_text(
        t("main_menu", lang),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang, is_admin),
    )
    return MAIN_MENU


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_lang(update.effective_user.id)
    is_admin = update.effective_user.id in ADMIN_IDS
    await query.edit_message_text(
        t("cancelled", lang) + "\n\n" + t("main_menu", lang),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang, is_admin),
    )
    return MAIN_MENU


async def cancel_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel typed manually during conversation."""
    await _delete_user_msg(update)
    lang = await get_lang(update.effective_user.id)
    is_admin = update.effective_user.id in ADMIN_IDS
    await _edit_or_send(
        update, context,
        t("cancelled", lang) + "\n\n" + t("main_menu", lang),
        reply_markup=main_menu_keyboard(lang, is_admin),
    )
    return MAIN_MENU


# ══════════════════════════════════════════════════════════════
#  Set Lovable Account
# ══════════════════════════════════════════════════════════════

async def set_lovable_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_lang(update.effective_user.id)
    await query.edit_message_text(
        t("lovable_prompt_email", lang),
        parse_mode="HTML",
        reply_markup=cancel_keyboard(lang),
    )
    return LOVABLE_EMAIL


async def lovable_email_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    await _delete_user_msg(update)
    lang = await get_lang(update.effective_user.id)
    context.user_data["lovable_email"] = email
    await _edit_or_send(
        update, context,
        t("lovable_prompt_password", lang),
        reply_markup=cancel_keyboard(lang),
    )
    return LOVABLE_PASS


async def lovable_pass_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    await _delete_user_msg(update)
    lang = await get_lang(update.effective_user.id)
    email = context.user_data.get("lovable_email", "")

    await db.set_lovable_account(update.effective_user.id, email, password)

    is_admin = update.effective_user.id in ADMIN_IDS
    await _edit_or_send(
        update, context,
        t("lovable_saved", lang) + "\n\n" + t("main_menu", lang),
        reply_markup=main_menu_keyboard(lang, is_admin),
    )
    return MAIN_MENU


# ══════════════════════════════════════════════════════════════
#  Submit Gmail
# ══════════════════════════════════════════════════════════════

async def submit_gmail_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    lang = await get_lang(user.id)

    # Must have Lovable account set first
    db_user = await db.get_user(user.id)
    if not db_user.get("lovable_email"):
        await query.edit_message_text(
            t("lovable_not_set", lang),
            parse_mode="HTML",
            reply_markup=back_keyboard(lang),
        )
        return MAIN_MENU

    await query.edit_message_text(
        t("gmail_prompt_email", lang),
        parse_mode="HTML",
        reply_markup=cancel_keyboard(lang),
    )
    return GMAIL_EMAIL


async def gmail_email_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip().lower()
    await _delete_user_msg(update)
    lang = await get_lang(update.effective_user.id)

    if not GMAIL_REGEX.match(email):
        await _edit_or_send(
            update, context,
            t("gmail_invalid", lang),
            reply_markup=cancel_keyboard(lang),
        )
        return GMAIL_EMAIL

    if await db.gmail_exists(email):
        await _edit_or_send(
            update, context,
            t("gmail_duplicate", lang),
            reply_markup=cancel_keyboard(lang),
        )
        return GMAIL_EMAIL

    context.user_data["gmail_email"] = email
    await _edit_or_send(
        update, context,
        t("gmail_prompt_password", lang),
        reply_markup=cancel_keyboard(lang),
    )
    return GMAIL_PASS


async def gmail_pass_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    email_for_submit = context.user_data.get("gmail_email", "")
    await _delete_user_msg(update)

    user = update.effective_user
    lang = await get_lang(user.id)

    await db.add_gmail(user.id, email_for_submit, password, POINTS_PER_GMAIL)
    await db.add_points(user.id, POINTS_PER_GMAIL)

    db_user = await db.get_user(user.id)
    balance_val = db_user["balance"]
    is_admin = user.id in ADMIN_IDS

    await _edit_or_send(
        update, context,
        t("gmail_success", lang, email=email_for_submit, points=POINTS_PER_GMAIL, balance=balance_val)
        + "\n\n" + t("main_menu", lang),
        reply_markup=main_menu_keyboard(lang, is_admin),
    )
    return MAIN_MENU


# ══════════════════════════════════════════════════════════════
#  My Account
# ══════════════════════════════════════════════════════════════

async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    lang = await get_lang(user.id)
    db_user = await db.get_user(user.id)

    lovable_status = f"<code>{db_user['lovable_email']}</code>" if db_user.get("lovable_email") else "❌ Not set"

    text = t(
        "account_info", lang,
        tid=user.id,
        name=db_user["full_name"],
        balance=db_user["balance"],
        gmails=db_user["gmails_submitted"],
        total=db_user["total_earned"],
        lovable=lovable_status,
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard(lang))
    return MAIN_MENU


# ══════════════════════════════════════════════════════════════
#  Balance
# ══════════════════════════════════════════════════════════════

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = await get_lang(update.effective_user.id)
    db_user = await db.get_user(update.effective_user.id)
    text = t("balance_info", lang, balance=db_user["balance"])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard(lang))
    return MAIN_MENU


# ══════════════════════════════════════════════════════════════
#  History
# ══════════════════════════════════════════════════════════════

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    lang = await get_lang(user.id)
    gmails = await db.get_user_gmails(user.id)

    if not gmails:
        await query.edit_message_text(
            t("history_empty", lang), parse_mode="HTML", reply_markup=back_keyboard(lang)
        )
        return MAIN_MENU

    text = t("history_header", lang)
    for g in gmails[:15]:
        date = g["submitted_at"].strftime("%Y-%m-%d %H:%M")
        text += t("history_item", lang, email=g["email"], points=g["points_awarded"], date=date)

    if len(gmails) > 15:
        more = len(gmails) - 15
        text += f"\n... +{more} more"

    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard(lang))
    return MAIN_MENU


# ══════════════════════════════════════════════════════════════
#  Withdraw
# ══════════════════════════════════════════════════════════════

async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    lang = await get_lang(user.id)
    db_user = await db.get_user(user.id)

    if not db_user.get("lovable_email"):
        await query.edit_message_text(
            t("lovable_not_set", lang), parse_mode="HTML", reply_markup=back_keyboard(lang)
        )
        return MAIN_MENU

    if db_user["balance"] <= 0:
        await query.edit_message_text(
            t("withdraw_no_balance", lang), parse_mode="HTML", reply_markup=back_keyboard(lang)
        )
        return MAIN_MENU

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("withdraw_confirm", lang), callback_data="withdraw_yes"),
            InlineKeyboardButton(t("btn_cancel", lang), callback_data="back_main"),
        ]
    ])
    text = t("withdraw_prompt", lang) + f"\n\n💎 Balance: <b>{db_user['balance']}</b> pts"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    return WITHDRAW_CONFIRM


async def withdraw_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    lang = await get_lang(user.id)
    db_user = await db.get_user(user.id)

    points = db_user["balance"]
    if points <= 0:
        await query.edit_message_text(
            t("withdraw_no_balance", lang), parse_mode="HTML", reply_markup=back_keyboard(lang)
        )
        return MAIN_MENU

    w_id = await db.create_withdrawal(user.id, points)
    await db.deduct_points(user.id, points)

    # Notify admins (separate notification messages)
    for admin_id in ADMIN_IDS:
        try:
            admin_text = (
                f"🔔 <b>New Withdrawal Request</b>\n\n"
                f"👤 User: {db_user['full_name']} (<code>{user.id}</code>)\n"
                f"💎 Points: <b>{points}</b>\n"
                f"🔑 Lovable: <code>{db_user.get('lovable_email', 'N/A')}</code>\n"
                f"🔑 Password: <code>{db_user.get('lovable_password', 'N/A')}</code>\n"
                f"🆔 WID: <code>{w_id}</code>"
            )
            admin_kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"w_approve_{w_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"w_reject_{w_id}"),
                ]
            ])
            await context.bot.send_message(admin_id, admin_text, parse_mode="HTML", reply_markup=admin_kb)
        except Exception:
            pass

    is_admin = user.id in ADMIN_IDS
    await query.edit_message_text(
        t("withdraw_success", lang) + "\n\n" + t("main_menu", lang),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang, is_admin),
    )
    return MAIN_MENU


# ══════════════════════════════════════════════════════════════
#  Build the ConversationHandler  (user + admin flows)
# ══════════════════════════════════════════════════════════════

def build_user_conversation() -> ConversationHandler:
    # Late import to avoid circular dependency
    from handlers_admin import (
        admin_panel, view_gmails, view_users, view_withdrawals,
        add_credit_start, add_credit_id_received, add_credit_amount_received,
        broadcast_start, broadcast_msg_received,
        ban_start, unban_start, ban_id_received, unban_id_received,
    )

    return ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            CHOOSE_LANG: [
                CallbackQueryHandler(language_chosen, pattern=r"^lang_(en|ar)$"),
                CallbackQueryHandler(back_to_main, pattern=r"^back_main$"),
            ],
            MAIN_MENU: [
                CallbackQueryHandler(submit_gmail_start, pattern=r"^submit_gmail$"),
                CallbackQueryHandler(my_account, pattern=r"^my_account$"),
                CallbackQueryHandler(balance, pattern=r"^balance$"),
                CallbackQueryHandler(history, pattern=r"^history$"),
                CallbackQueryHandler(set_lovable_start, pattern=r"^set_lovable$"),
                CallbackQueryHandler(withdraw_start, pattern=r"^withdraw$"),
                CallbackQueryHandler(change_lang_callback, pattern=r"^change_lang$"),
                CallbackQueryHandler(admin_panel, pattern=r"^admin_panel$"),
                CallbackQueryHandler(back_to_main, pattern=r"^back_main$"),
            ],
            LOVABLE_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, lovable_email_received),
                CallbackQueryHandler(cancel_callback, pattern=r"^cancel$"),
            ],
            LOVABLE_PASS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, lovable_pass_received),
                CallbackQueryHandler(cancel_callback, pattern=r"^cancel$"),
            ],
            GMAIL_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gmail_email_received),
                CallbackQueryHandler(cancel_callback, pattern=r"^cancel$"),
            ],
            GMAIL_PASS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gmail_pass_received),
                CallbackQueryHandler(cancel_callback, pattern=r"^cancel$"),
            ],
            WITHDRAW_CONFIRM: [
                CallbackQueryHandler(withdraw_confirmed, pattern=r"^withdraw_yes$"),
                CallbackQueryHandler(back_to_main, pattern=r"^back_main$"),
            ],
            # ── Admin states ──────────────────────────────────
            ADMIN_MENU: [
                CallbackQueryHandler(view_gmails, pattern=r"^adm_gmails$"),
                CallbackQueryHandler(view_users, pattern=r"^adm_users$"),
                CallbackQueryHandler(view_withdrawals, pattern=r"^adm_withdrawals$"),
                CallbackQueryHandler(add_credit_start, pattern=r"^adm_add_credit$"),
                CallbackQueryHandler(broadcast_start, pattern=r"^adm_broadcast$"),
                CallbackQueryHandler(ban_start, pattern=r"^adm_ban$"),
                CallbackQueryHandler(unban_start, pattern=r"^adm_unban$"),
                CallbackQueryHandler(admin_panel, pattern=r"^admin_panel$"),
                CallbackQueryHandler(back_to_main, pattern=r"^back_main$"),
            ],
            ADM_CREDIT_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_credit_id_received),
                CallbackQueryHandler(admin_panel, pattern=r"^admin_panel$"),
            ],
            ADM_CREDIT_AMT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_credit_amount_received),
                CallbackQueryHandler(admin_panel, pattern=r"^admin_panel$"),
            ],
            ADM_BAN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ban_id_received),
                CallbackQueryHandler(admin_panel, pattern=r"^admin_panel$"),
            ],
            ADM_UNBAN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, unban_id_received),
                CallbackQueryHandler(admin_panel, pattern=r"^admin_panel$"),
            ],
            ADM_BROADCAST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_msg_received),
                CallbackQueryHandler(admin_panel, pattern=r"^admin_panel$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_text),
            CommandHandler("start", start_command),
        ],
        allow_reentry=True,
    )
