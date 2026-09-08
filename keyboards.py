from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# Asosiy menyu tugmalari
def get_main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="📩 Shikoyat / Murojaat yo'llash")],
        [KeyboardButton(text="ℹ️ Bot haqida"), KeyboardButton(text="📞 ISFT bilan bog'lanish")]
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="⚙️ Admin panel")])
        
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Quyidagi tugmalardan birini tanlang..."
    )

# 1-qadam: Aloqa operatorini tanlash (Inline tugmalar)
def get_departments_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📞 Aloqa operatori", callback_data="dept_callcenter")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_complaint")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 2-qadam: Call center operatori bo'yicha shikoyat sababini tanlash
def get_reasons_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="⏳ Vaqtida javob berilmadi", callback_data="reason_not_on_time")],
        [InlineKeyboardButton(text="❓ Aniq javob berilmadi", callback_data="reason_unclear_answer")],
        [InlineKeyboardButton(text="⏱ Suhbat vaqtida juda uzoq kuttirdi", callback_data="reason_hold_long")],
        [InlineKeyboardButton(text="🗣 Muomala madaniyati talabga javob bermadi", callback_data="reason_rude")],
        [InlineKeyboardButton(text="📴 Qo'ng'iroqni asossiz uzib qo'ydi", callback_data="reason_disconnect")],
        [InlineKeyboardButton(text="🔄 Masalani hal qilmay sarson qildi", callback_data="reason_delay")],
        [InlineKeyboardButton(text="📵 Ish vaqtida bog'lanib bo'lmadi", callback_data="reason_unreachable")],
        [InlineKeyboardButton(text="✍️ Boshqa", callback_data="reason_custom")],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_dept"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_complaint")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Ortga yoki bekor qilish tugmasi
def get_back_to_reason_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_reason"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_complaint")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 3-qadam: Holat haqida qo'shimcha tafsilot (Button orqali tezkor tanlov)
def get_details_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📅 Bugun sodir bo'ldi", callback_data="detail_today")],
        [InlineKeyboardButton(text="🔁 Bir necha bor takrorlandi", callback_data="detail_repeated")],
        [InlineKeyboardButton(text="⏳ Bir necha kundan beri hal bo'lmayapti", callback_data="detail_few_days")],
        [InlineKeyboardButton(text="🚨 O'ta muhim va shoshilinch masala", callback_data="detail_urgent")],
        [InlineKeyboardButton(text="✍️ O'z so'zim bilan yozish", callback_data="detail_write_text")],
        [InlineKeyboardButton(text="⏩ Qo'shimcha izohsiz davom etish", callback_data="detail_skip")],
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_reason"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_complaint")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Bog'lanish raqamini yuborish tugmalari
def get_phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📲 Telefon raqamimni yuborish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# 5-qadam: Tasdiqlash va yuborish
def get_confirmation_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_send"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_complaint")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Admin panel tugmalari
def get_admin_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📊 Umumiy statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🆕 Yangi shikoyatlar", callback_data="admin_new_complaints")],
        [InlineKeyboardButton(text="📋 Oxirgi 10 ta shikoyat", callback_data="admin_recent_complaints")],
        [InlineKeyboardButton(text="🔙 Menyuga qaytish", callback_data="admin_close")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Admin shikoyatni boshqarish tugmasi
def get_complaint_action_kb(complaint_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🔍 Ko'rib chiqilmoqda", callback_data=f"status_{complaint_id}_review"),
            InlineKeyboardButton(text="✅ Hal etildi", callback_data=f"status_{complaint_id}_resolved")
        ],
        [InlineKeyboardButton(text="⬅️ Ro'yxatga qaytish", callback_data="admin_recent_complaints")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
