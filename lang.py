# ══════════════════════════════════════════════════════════════
#  Bilingual strings  –  English / Arabic
# ══════════════════════════════════════════════════════════════

STRINGS = {
    # ── Welcome & Main Menu ───────────────────────────────────
    "welcome": {
        "en": (
            "🌟 <b>Welcome to Lovable Credits Bot!</b>\n\n"
            "Submit Gmail accounts and earn <b>Lovable credits</b> "
            "directly to your account.\n\n"
            "🔹 <b>100 points</b> for every Gmail you submit\n"
            "🔹 Instant credit — no waiting\n"
            "🔹 Track your balance anytime\n\n"
            "Choose your language to get started 👇"
        ),
        "ar": (
            "🌟 <b>مرحبًا بك في بوت رصيد Lovable!</b>\n\n"
            "أرسل حسابات Gmail واحصل على <b>رصيد Lovable</b> "
            "مباشرة في حسابك.\n\n"
            "🔹 <b>100 نقطة</b> لكل Gmail ترسله\n"
            "🔹 رصيد فوري — بدون انتظار\n"
            "🔹 تتبع رصيدك في أي وقت\n\n"
            "اختر لغتك للبدء 👇"
        ),
    },

    "main_menu": {
        "en": (
            "📋 <b>Main Menu</b>\n\n"
            "What would you like to do?"
        ),
        "ar": (
            "📋 <b>القائمة الرئيسية</b>\n\n"
            "ماذا تريد أن تفعل؟"
        ),
    },

    # ── Buttons ────────────────────────────────────────────────
    "btn_submit_gmail": {"en": "📧 Submit Gmail", "ar": "📧 إرسال Gmail"},
    "btn_my_account": {"en": "👤 My Account", "ar": "👤 حسابي"},
    "btn_balance": {"en": "💰 Balance", "ar": "💰 الرصيد"},
    "btn_history": {"en": "📜 History", "ar": "📜 السجل"},
    "btn_set_lovable": {"en": "🔑 Set Lovable Account", "ar": "🔑 تعيين حساب Lovable"},
    "btn_language": {"en": "🌐 Language", "ar": "🌐 اللغة"},
    "btn_back": {"en": "◀️ Back", "ar": "◀️ رجوع"},
    "btn_cancel": {"en": "❌ Cancel", "ar": "❌ إلغاء"},
    "btn_support": {"en": "💬 Support", "ar": "💬 الدعم"},
    "btn_withdraw": {"en": "🎁 Withdraw Credits", "ar": "🎁 سحب الرصيد"},

    # ── Language ───────────────────────────────────────────────
    "choose_lang": {
        "en": "🌐 Choose your language:",
        "ar": "🌐 اختر لغتك:",
    },
    "lang_set": {
        "en": "✅ Language set to <b>English</b>.",
        "ar": "✅ تم تعيين اللغة إلى <b>العربية</b>.",
    },

    # ── Lovable Account ────────────────────────────────────────
    "lovable_prompt_email": {
        "en": "📧 Send your <b>Lovable account email</b>:",
        "ar": "📧 أرسل <b>بريد حساب Lovable</b> الخاص بك:",
    },
    "lovable_prompt_password": {
        "en": "🔒 Now send your <b>Lovable account password</b>:\n\n<i>Your data is stored securely.</i>",
        "ar": "🔒 الآن أرسل <b>كلمة مرور حساب Lovable</b>:\n\n<i>بياناتك محفوظة بأمان.</i>",
    },
    "lovable_saved": {
        "en": "✅ Lovable account saved successfully!",
        "ar": "✅ تم حفظ حساب Lovable بنجاح!",
    },
    "lovable_not_set": {
        "en": "⚠️ You haven't set your Lovable account yet.\nPlease set it first using <b>🔑 Set Lovable Account</b>.",
        "ar": "⚠️ لم تقم بتعيين حساب Lovable بعد.\nيرجى تعيينه أولاً باستخدام <b>🔑 تعيين حساب Lovable</b>.",
    },

    # ── Gmail Submission ───────────────────────────────────────
    "gmail_prompt_email": {
        "en": "📧 Send the <b>Gmail address</b> you want to submit:",
        "ar": "📧 أرسل <b>عنوان Gmail</b> الذي تريد إرساله:",
    },
    "gmail_prompt_password": {
        "en": "🔒 Now send the <b>password</b> for this Gmail:",
        "ar": "🔒 الآن أرسل <b>كلمة المرور</b> لهذا Gmail:",
    },
    "gmail_duplicate": {
        "en": "⚠️ This Gmail has already been submitted. Try a different one.",
        "ar": "⚠️ تم إرسال هذا Gmail مسبقًا. جرب واحدًا آخر.",
    },
    "gmail_invalid": {
        "en": "❌ Invalid Gmail format. Please send a valid <b>@gmail.com</b> address.",
        "ar": "❌ صيغة Gmail غير صالحة. أرسل عنوانًا صالحًا <b>@gmail.com</b>.",
    },
    "gmail_success": {
        "en": (
            "✅ <b>Gmail accepted!</b>\n\n"
            "📧 Gmail: <code>{email}</code>\n"
            "💰 Points earned: <b>+{points}</b>\n"
            "💎 New balance: <b>{balance}</b> pts\n\n"
            "Keep submitting to earn more!"
        ),
        "ar": (
            "✅ <b>تم قبول Gmail!</b>\n\n"
            "📧 Gmail: <code>{email}</code>\n"
            "💰 النقاط المكتسبة: <b>+{points}</b>\n"
            "💎 الرصيد الجديد: <b>{balance}</b> نقطة\n\n"
            "استمر في الإرسال لكسب المزيد!"
        ),
    },

    # ── Account / Balance ──────────────────────────────────────
    "account_info": {
        "en": (
            "👤 <b>Your Account</b>\n\n"
            "┌─────────────────────────\n"
            "│ 🆔 ID: <code>{tid}</code>\n"
            "│ 👤 Name: {name}\n"
            "│ 💎 Balance: <b>{balance}</b> pts\n"
            "│ 📧 Gmails sent: <b>{gmails}</b>\n"
            "│ 🏆 Total earned: <b>{total}</b> pts\n"
            "│ 🔑 Lovable: {lovable}\n"
            "└─────────────────────────"
        ),
        "ar": (
            "👤 <b>حسابك</b>\n\n"
            "┌─────────────────────────\n"
            "│ 🆔 المعرّف: <code>{tid}</code>\n"
            "│ 👤 الاسم: {name}\n"
            "│ 💎 الرصيد: <b>{balance}</b> نقطة\n"
            "│ 📧 Gmail مُرسل: <b>{gmails}</b>\n"
            "│ 🏆 الإجمالي: <b>{total}</b> نقطة\n"
            "│ 🔑 Lovable: {lovable}\n"
            "└─────────────────────────"
        ),
    },
    "balance_info": {
        "en": "💰 Your balance: <b>{balance}</b> points",
        "ar": "💰 رصيدك: <b>{balance}</b> نقطة",
    },

    # ── History ────────────────────────────────────────────────
    "history_empty": {
        "en": "📜 You haven't submitted any Gmail yet.",
        "ar": "📜 لم ترسل أي Gmail بعد.",
    },
    "history_header": {
        "en": "📜 <b>Your Submission History</b>\n\n",
        "ar": "📜 <b>سجل إرسالاتك</b>\n\n",
    },
    "history_item": {
        "en": "📧 <code>{email}</code>  →  +{points} pts  •  {date}\n",
        "ar": "📧 <code>{email}</code>  →  +{points} نقطة  •  {date}\n",
    },

    # ── Withdraw ───────────────────────────────────────────────
    "withdraw_prompt": {
        "en": "🎁 Your credits will be added to your Lovable account.\nClick confirm to proceed.",
        "ar": "🎁 سيتم إضافة رصيدك إلى حساب Lovable الخاص بك.\nاضغط تأكيد للمتابعة.",
    },
    "withdraw_confirm": {"en": "✅ Confirm", "ar": "✅ تأكيد"},
    "withdraw_success": {
        "en": "✅ Withdrawal request submitted! An admin will process it shortly.",
        "ar": "✅ تم إرسال طلب السحب! سيقوم المسؤول بمعالجته قريبًا.",
    },
    "withdraw_no_balance": {
        "en": "❌ You have no points to withdraw.",
        "ar": "❌ ليس لديك نقاط للسحب.",
    },

    # ── Misc ───────────────────────────────────────────────────
    "banned": {
        "en": "🚫 Your account has been banned. Contact support.",
        "ar": "🚫 تم حظر حسابك. تواصل مع الدعم.",
    },
    "cancelled": {
        "en": "❌ Operation cancelled.",
        "ar": "❌ تم إلغاء العملية.",
    },
    "support_msg": {
        "en": "💬 For support, contact: {support}",
        "ar": "💬 للدعم، تواصل مع: {support}",
    },

    # ── Admin ──────────────────────────────────────────────────
    "admin_panel": {
        "en": (
            "🛠 <b>Admin Panel</b>\n\n"
            "👥 Total users: <b>{users}</b>\n"
            "📧 Total Gmails: <b>{gmails}</b>\n"
            "⏳ Pending withdrawals: <b>{pending}</b>"
        ),
        "ar": (
            "🛠 <b>لوحة الإدارة</b>\n\n"
            "👥 المستخدمون: <b>{users}</b>\n"
            "📧 Gmail: <b>{gmails}</b>\n"
            "⏳ طلبات معلقة: <b>{pending}</b>"
        ),
    },
    "btn_admin_panel": {"en": "🛠 Admin Panel", "ar": "🛠 لوحة الإدارة"},
    "btn_view_gmails": {"en": "📧 View Gmails", "ar": "📧 عرض Gmail"},
    "btn_view_users": {"en": "👥 View Users", "ar": "👥 عرض المستخدمين"},
    "btn_withdrawals": {"en": "🎁 Withdrawals", "ar": "🎁 طلبات السحب"},
    "btn_add_credit": {"en": "💳 Add Credit", "ar": "💳 إضافة رصيد"},
    "btn_broadcast": {"en": "📢 Broadcast", "ar": "📢 بث رسالة"},
    "btn_ban_user": {"en": "🚫 Ban User", "ar": "🚫 حظر مستخدم"},
    "btn_unban_user": {"en": "✅ Unban User", "ar": "✅ إلغاء الحظر"},
    "btn_approve": {"en": "✅ Approve", "ar": "✅ موافقة"},
    "btn_reject": {"en": "❌ Reject", "ar": "❌ رفض"},

    "broadcast_prompt": {
        "en": "📢 Send the message you want to broadcast to all users:",
        "ar": "📢 أرسل الرسالة التي تريد بثها لجميع المستخدمين:",
    },
    "broadcast_done": {
        "en": "✅ Broadcast sent to <b>{count}</b> users.",
        "ar": "✅ تم البث إلى <b>{count}</b> مستخدم.",
    },
    "ban_prompt": {
        "en": "🚫 Send the Telegram ID of the user to ban:",
        "ar": "🚫 أرسل معرّف Telegram للمستخدم المراد حظره:",
    },
    "unban_prompt": {
        "en": "✅ Send the Telegram ID of the user to unban:",
        "ar": "✅ أرسل معرّف Telegram للمستخدم المراد إلغاء حظره:",
    },
    "ban_done": {
        "en": "✅ User <code>{tid}</code> has been banned.",
        "ar": "✅ تم حظر المستخدم <code>{tid}</code>.",
    },
    "unban_done": {
        "en": "✅ User <code>{tid}</code> has been unbanned.",
        "ar": "✅ تم إلغاء حظر المستخدم <code>{tid}</code>.",
    },
    "user_not_found": {
        "en": "❌ User not found.",
        "ar": "❌ المستخدم غير موجود.",
    },
    "not_admin": {
        "en": "⛔ You are not authorized.",
        "ar": "⛔ ليس لديك صلاحية.",
    },

    # ── Add Credit (Admin) ─────────────────────────────────────
    "add_credit_prompt_id": {
        "en": "💳 Send the <b>Telegram ID</b> of the user to add Lovable credit to:",
        "ar": "💳 أرسل <b>معرّف Telegram</b> للمستخدم لإضافة رصيد Lovable له:",
    },
    "add_credit_prompt_amount": {
        "en": (
            "👤 User: <b>{name}</b>\n"
            "🆔 ID: <code>{tid}</code>\n"
            "🔑 Lovable: <code>{lovable}</code>\n\n"
            "💳 Send the <b>amount of credits</b> to add:"
        ),
        "ar": (
            "👤 المستخدم: <b>{name}</b>\n"
            "🆔 المعرّف: <code>{tid}</code>\n"
            "🔑 Lovable: <code>{lovable}</code>\n\n"
            "💳 أرسل <b>عدد الرصيد</b> المراد إضافته:"
        ),
    },
    "add_credit_done": {
        "en": "✅ Successfully added <b>{amount}</b> Lovable credits to <b>{name}</b>!\n\nUser has been notified. ✉️",
        "ar": "✅ تم إضافة <b>{amount}</b> رصيد Lovable بنجاح لـ <b>{name}</b>!\n\nتم إخطار المستخدم. ✉️",
    },
    "add_credit_invalid_amount": {
        "en": "❌ Invalid amount. Please send a valid number.",
        "ar": "❌ مبلغ غير صالح. أرسل رقمًا صحيحًا.",
    },

    # ── User Notifications ─────────────────────────────────────
    "notify_credit_added": {
        "en": (
            "🎉🎉🎉🎉🎉🎉🎉🎉\n\n"
            "💎 <b>CREDITS ADDED!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💳 Amount: <b>{amount} credits</b>\n"
            "🔑 Account: <code>{lovable}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ Lovable credits have been added to\n"
            "your account successfully!\n\n"
            "Thank you for using our service! 🌟\n"
            "Keep submitting Gmails to earn more! 📧"
        ),
        "ar": (
            "🎉🎉🎉🎉🎉🎉🎉🎉\n\n"
            "💎 <b>تمت إضافة الرصيد!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💳 المبلغ: <b>{amount} رصيد</b>\n"
            "🔑 الحساب: <code>{lovable}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ تم إضافة رصيد Lovable إلى حسابك\n"
            "بنجاح!\n\n"
            "شكرًا لاستخدامك خدمتنا! 🌟\n"
            "استمر في إرسال Gmail لكسب المزيد! 📧"
        ),
    },
    "notify_withdrawal_approved": {
        "en": (
            "🎉🎉🎉🎉🎉🎉🎉🎉\n\n"
            "✅ <b>WITHDRAWAL APPROVED!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💎 Points: <b>{points}</b>\n"
            "🔑 Account: <code>{lovable}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Your Lovable credits have been added\n"
            "to your account! Enjoy! 🚀"
        ),
        "ar": (
            "🎉🎉🎉🎉🎉🎉🎉🎉\n\n"
            "✅ <b>تمت الموافقة على السحب!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💎 النقاط: <b>{points}</b>\n"
            "🔑 الحساب: <code>{lovable}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "تم إضافة رصيد Lovable إلى حسابك!\n"
            "استمتع! 🚀"
        ),
    },
    "notify_withdrawal_rejected": {
        "en": (
            "❌ <b>Withdrawal Rejected</b>\n\n"
            "Your withdrawal of <b>{points}</b> points was rejected.\n"
            "Points have been refunded to your balance.\n\n"
            "Contact support if you have questions."
        ),
        "ar": (
            "❌ <b>تم رفض السحب</b>\n\n"
            "تم رفض طلب سحب <b>{points}</b> نقطة.\n"
            "تم إرجاع النقاط إلى رصيدك.\n\n"
            "تواصل مع الدعم إذا كان لديك أسئلة."
        ),
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Get translated string. Falls back to English."""
    entry = STRINGS.get(key, {})
    text = entry.get(lang, entry.get("en", key))
    if kwargs:
        text = text.format(**kwargs)
    return text
