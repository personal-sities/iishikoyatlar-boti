from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
import database
import keyboards

router = Router()

# FSM holatlari
class ComplaintFSM(StatesGroup):
    department = State()
    reason = State()
    custom_reason = State()
    details = State()
    custom_details = State()
    student_name = State()
    student_id = State()
    phone = State()
    confirm = State()

DEPARTMENTS = {
    "dept_callcenter": "📞 Aloqa operatori"
}

REASONS = {
    "reason_not_on_time": "⏳ Vaqtida javob berilmadi",
    "reason_unclear_answer": "❓ Aniq javob berilmadi",
    "reason_hold_long": "⏱ Suhbat vaqtida juda uzoq kuttirdi",
    "reason_rude": "🗣 Muomala madaniyati talabga javob bermadi",
    "reason_disconnect": "📴 Qo'ng'iroqni asossiz uzib qo'ydi",
    "reason_delay": "🔄 Masalani hal qilmay sarson qildi",
    "reason_unreachable": "📵 Ish vaqtida bog'lanib bo'lmadi",
    "reason_custom": "✍️ Boshqa Call-center e'tirozi"
}

DETAILS = {
    "detail_today": "📅 Bugun sodir bo'ldi",
    "detail_repeated": "🔁 Bir necha bor takrorlandi",
    "detail_few_days": "⏳ Bir necha kundan beri hal bo'lmayapti",
    "detail_urgent": "🚨 O'ta muhim va shoshilinch masala",
    "detail_skip": "— (Qo'shimcha izohsiz)"
}

# Start buyrug'i
@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    database.save_user(user.id, user.full_name, user.username)
    
    is_admin = user.id in ADMIN_IDS
    welcome_text = (
        f"Assalomu alaykum, <b>{user.full_name}</b>!\n\n"
        f"🏛 <b>ISFT Instituti Yagona aloqa operatorlari rahbarining botiga xush kelibsiz.</b>\n\n"
        f"Ushbu bot orqali faqat ISFT instituti <b>Yagona aloqa operatorlari</b> faoliyati yuzasidan "
        f"o'z shikoyat, e'tiroz va takliflaringizni bevosita <b>operatorlar rahbariga</b> yo'llashingiz mumkin.\n\n"
        f"Barcha bosqichlar qulay tugmalar orqali amalga oshiriladi.\n"
        f"Murojaat qoldirish uchun pastdagi <b>«📩 Shikoyat / Murojaat yo'llash»</b> tugmasini bosing."
    )
    await message.answer(welcome_text, reply_markup=keyboards.get_main_menu(is_admin), parse_mode="HTML")

# Shikoyat jarayonini boshlash
@router.message(F.text == "📩 Shikoyat / Murojaat yo'llash")
async def start_complaint(message: Message, state: FSMContext):
    await state.set_state(ComplaintFSM.department)
    text = (
        "<b>1-bosqich:</b> Qaysi yagona aloqa operatori xizmati bo'yicha e'tirozingiz bor?\n\n"
        "Quyidagi tugmalardan birini tanlang:"
    )
    await message.answer(text, reply_markup=keyboards.get_departments_kb(), parse_mode="HTML")

# Bekor qilish tugmasi (Callback)
@router.callback_query(F.data == "cancel_complaint")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    is_admin = callback.from_user.id in ADMIN_IDS
    await callback.message.delete()
    await callback.message.answer(
        "❌ Murojaat bekor qilindi.",
        reply_markup=keyboards.get_main_menu(is_admin)
    )
    await callback.answer()

# Bekor qilish matn tugmasi
@router.message(F.text == "❌ Bekor qilish")
async def cancel_text(message: Message, state: FSMContext):
    await state.clear()
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer(
        "❌ Murojaat bekor qilindi.",
        reply_markup=keyboards.get_main_menu(is_admin)
    )

# Bo'lim tanlanganda (1-qadam)
@router.callback_query(ComplaintFSM.department, F.data.startswith("dept_"))
async def choose_department(callback: CallbackQuery, state: FSMContext):
    dept_code = callback.data
    dept_name = DEPARTMENTS.get(dept_code, "Noma'lum operator")
    await state.update_data(department=dept_name)
    
    await state.set_state(ComplaintFSM.reason)
    text = (
        f"Tanlangan operator: <b>{dept_name}</b>\n\n"
        f"<b>2-bosqich:</b> E'tiroz yoki shikoyatning asosiy sababi nima?\n\n"
        f"Tugmalardan mosini tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=keyboards.get_reasons_kb(), parse_mode="HTML")
    await callback.answer()

# Ortga: operator tanlashga qaytish
@router.callback_query(F.data == "back_to_dept")
async def back_to_dept(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ComplaintFSM.department)
    text = (
        "<b>1-bosqich:</b> Qaysi yagona aloqa operatori xizmati bo'yicha e'tirozingiz bor?\n\n"
        "Quyidagi tugmalardan birini tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=keyboards.get_departments_kb(), parse_mode="HTML")
    await callback.answer()

# Shikoyat sababi tanlanganda (2-qadam)
@router.callback_query(ComplaintFSM.reason, F.data.startswith("reason_"))
async def choose_reason(callback: CallbackQuery, state: FSMContext):
    reason_code = callback.data
    
    if reason_code == "reason_custom":
        await state.set_state(ComplaintFSM.custom_reason)
        text = (
            "✍️ <b>Shikoyat yoki e'tirozingizni yozma ravishda bayon qiling:</b>\n\n"
            "Iltimos, yuz bergan holatni batafsil yozib yuboring:"
        )
        await callback.message.edit_text(text, reply_markup=keyboards.get_back_to_reason_kb(), parse_mode="HTML")
        await callback.answer()
        return

    reason_name = REASONS.get(reason_code, "Boshqa")
    await state.update_data(reason=reason_name)
    
    await state.set_state(ComplaintFSM.details)
    text = (
        f"Shikoyat sababi: <b>{reason_name}</b>\n\n"
        f"<b>3-bosqich:</b> Holat haqida qo'shimcha ma'lumotni tugma orqali belgilang:"
    )
    await callback.message.edit_text(text, reply_markup=keyboards.get_details_kb(), parse_mode="HTML")
    await callback.answer()

# Boshqa sabab qo'lda yozilganda
@router.message(ComplaintFSM.custom_reason, F.text)
async def handle_custom_reason(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_text(message, state)
        return
    custom_reason_text = message.text.strip()
    await state.update_data(reason="Boshqa (Yozma e'tiroz)", details=custom_reason_text)
    await ask_student_name(message, state)

# Ortga: sabab tanlashga qaytish
@router.callback_query(F.data == "back_to_reason")
async def back_to_reason(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ComplaintFSM.reason)
    data = await state.get_data()
    dept_name = data.get("department", "Tanlangan operator")
    text = (
        f"Tanlangan operator: <b>{dept_name}</b>\n\n"
        f"<b>2-bosqich:</b> E'tiroz yoki shikoyatning asosiy sababi nima?\n\n"
        f"Tugmalardan mosini tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=keyboards.get_reasons_kb(), parse_mode="HTML")
    await callback.answer()

# Tafsilotlar tugmasi bosilganda (3-qadam)
@router.callback_query(ComplaintFSM.details, F.data.startswith("detail_"))
async def choose_detail(callback: CallbackQuery, state: FSMContext):
    detail_code = callback.data
    
    if detail_code == "detail_write_text":
        await state.set_state(ComplaintFSM.custom_details)
        await callback.message.edit_text(
            "✍️ Iltimos, qo'shimcha tafsilotlarni yozma xabar tarzida yuboring:",
            reply_markup=keyboards.get_back_to_reason_kb(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    detail_name = DETAILS.get(detail_code, "—")
    await state.update_data(details=detail_name)
    await callback.message.delete()
    await ask_student_name(callback.message, state)
    await callback.answer()

# Tafsilotlar qo'lda yozilganda
@router.message(ComplaintFSM.custom_details, F.text)
async def handle_custom_details(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_text(message, state)
        return
    await state.update_data(details=message.text.strip())
    await ask_student_name(message, state)

# Ism-familiya so'rash yordamchi funksiyasi
async def ask_student_name(message: Message, state: FSMContext):
    await state.set_state(ComplaintFSM.student_name)
    text = (
        "👤 <b>Iltimos, ism va familiyangizni kiriting:</b>\n\n"
        "<i>(Masalan: Karimov Sardor)</i>"
    )
    await message.answer(text, reply_markup=keyboards.get_back_to_reason_kb(), parse_mode="HTML")

# 1. Ism-familiya qabul qilish
@router.message(ComplaintFSM.student_name, F.text)
async def handle_student_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_text(message, state)
        return
    name = message.text.strip()
    await state.update_data(student_name=name)
    
    await state.set_state(ComplaintFSM.student_id)
    text = (
        f"Rahmat, <b>{name}</b>!\n\n"
        "🎓 <b>Talabalik ID raqamingizni kiriting:</b>\n\n"
        "<i>(Talabalik guvohnomangiz yoki HEMIS tizimidagi ID raqamingizni yozib yuboring)</i>"
    )
    await message.answer(text, reply_markup=keyboards.get_back_to_reason_kb(), parse_mode="HTML")

# 2. Talabalik ID raqami qabul qilish
@router.message(ComplaintFSM.student_id, F.text)
async def handle_student_id(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_text(message, state)
        return
    st_id = message.text.strip()
    await state.update_data(student_id=st_id)
    
    await state.set_state(ComplaintFSM.phone)
    text = (
        "📞 <b>Qaysi telefon raqamingiz bilan biz bilan (operator bilan) bog'langan edingiz?</b>\n\n"
        "Quyidagi tugmani bosing yoki raqamingizni yozib yuboring:"
    )
    await message.answer(text, reply_markup=keyboards.get_phone_kb(), parse_mode="HTML")

# 3. Bog'lanilgan telefon raqami yuborilganda (Contact orqali)
@router.message(ComplaintFSM.phone, F.contact)
async def handle_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    await state.update_data(phone=phone)
    await show_confirmation(message, state)

# 4. Bog'lanilgan telefon raqami matn tarzida yuborilganda
@router.message(ComplaintFSM.phone, F.text)
async def handle_phone_text(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await cancel_text(message, state)
        return
    await state.update_data(phone=message.text.strip())
    await show_confirmation(message, state)

# Tasdiqlash bosqichi
async def show_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()
    department = data.get("department", "Aloqa operatori")
    reason = data.get("reason", "Noma'lum")
    details = data.get("details", "—")
    student_name = data.get("student_name", "Noma'lum")
    student_id = data.get("student_id", "Noma'lum")
    phone = data.get("phone", "Ko'rsatilmadi")
    
    await state.set_state(ComplaintFSM.confirm)
    
    summary_text = (
        "📋 <b>Murojaat ma'lumotlarini tasdiqlang:</b>\n\n"
        f"🏛 <b>Yagona aloqa operatori:</b> {department}\n"
        f"⚠️ <b>Shikoyat sababi:</b> {reason}\n"
        f"📝 <b>Qo'shimcha tafsilot:</b> {details}\n"
        f"👤 <b>Talaba:</b> {student_name}\n"
        f"🎓 <b>Talabalik ID:</b> <code>{student_id}</code>\n"
        f"📞 <b>Bog'lanilgan raqam:</b> {phone}\n\n"
        "Ma'lumotlar to'g'ri bo'lsa, <b>«✅ Yuborish»</b> tugmasini bosing:"
    )
    
    await message.answer("Murojaat tayyorlandi.", reply_markup=ReplyKeyboardRemove())
    await message.answer(summary_text, reply_markup=keyboards.get_confirmation_kb(), parse_mode="HTML")

# Yakuniy yuborish (Confirm Send)
@router.callback_query(ComplaintFSM.confirm, F.data == "confirm_send")
async def confirm_and_send(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user = callback.from_user
    
    department = data.get("department", "Aloqa operatori")
    reason = data.get("reason", "Noma'lum")
    details = data.get("details", "—")
    student_name = data.get("student_name", user.full_name)
    student_id = data.get("student_id", "Noma'lum")
    phone = data.get("phone", "Ko'rsatilmadi")
    
    # Bazaga yozish
    complaint_id = database.add_complaint(
        user_id=user.id,
        full_name=student_name,
        username=user.username,
        phone=phone,
        department=department,
        reason=reason,
        details=details,
        student_id=student_id
    )
    
    # Adminlarga va 5473259177 ga yuborish
    admin_notify_text = (
        f"🔔 <b>YANGI MUROJAAT #{complaint_id}</b>\n"
        f"🏛 <b>ISFT Yagona aloqa operatorlari rahbari uchun</b>\n\n"
        f"👤 <b>Talaba (F.I.SH):</b> {student_name}\n"
        f"🎓 <b>Talabalik ID:</b> <code>{student_id}</code>\n"
        f"📞 <b>Bog'lanilgan raqam:</b> {phone}\n"
        f"📱 <b>Telegram profili:</b> {user.full_name} (@{user.username if user.username else 'yo‘q'})\n"
        f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n"
        f"🏛 <b>Operator:</b> {department}\n"
        f"⚠️ <b>Shikoyat sababi:</b> {reason}\n"
        f"📝 <b>Tafsilot:</b> {details}\n"
        f"⏰ <b>Vaqti:</b> Hozir"
    )
    
    dest_chats = set(ADMIN_IDS)
    dest_chats.add(5473259177)
    
    for chat_id in dest_chats:
        try:
            await bot.send_message(
                chat_id, 
                admin_notify_text, 
                reply_markup=keyboards.get_complaint_action_kb(complaint_id),
                parse_mode="HTML"
            )
        except Exception:
            pass # Chat ID mavjud bo'lmasa yoki bot hali start qilinmagan bo'lsa
            
    await state.clear()
    await callback.message.delete()
    
    # Talabaga ko'rsatiladigan yakuniy xabar
    final_text = (
        "✅ <b>Sizning murojaatingiz qabul qilindi, tegishli tartibda choralar ko'riladi.</b>\n\n"
        "📞 Murojaat javobini operatorlarimiz sizga aloqaga chiqib xabar qiladi."
    )
    is_admin = (user.id in ADMIN_IDS) or (user.id == 5473259177)
    await callback.message.answer(final_text, reply_markup=keyboards.get_main_menu(is_admin), parse_mode="HTML")
    await callback.answer()

# Bot haqida va aloqa ma'lumotlari
@router.message(F.text == "ℹ️ Bot haqida")
async def about_bot(message: Message):
    text = (
        "ℹ️ <b>ISFT Instituti Yagona aloqa operatorlari rahbarining boti</b>\n\n"
        "Ushbu bot faqat ISFT instituti <b>Yagona aloqa operatorlari</b> faoliyati bo'yicha "
        "talabalarning shikoyat, e'tiroz va takliflarini to'g'ridan-to'g'ri <b>operatorlar rahbariga</b> "
        "yetkazish hamda xizmat ko'rsatish sifatini oshirish maqsadida ishlab chiqilgan.\n\n"
        "Barcha murojaatlar shaxsan Yagona aloqa operatorlari rahbari tomonidan qat'iy nazoratga olinadi "
        "va tegishli tartibda choralar ko'riladi."
    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "📞 ISFT bilan bog'lanish")
async def contact_info(message: Message):
    text = (
        "📞 <b>ISFT Instituti rasmiy aloqa vositalari:</b>\n\n"
        "🤖 Talabalar boti: @isftstudents_bot\n"
        "☎️ Telefon raqam: +998 (55) 508-37-37\n"
        "📍 Manzil: Toshkent shahri Mirzo Ulug'bek tumani, Bahor MFY 122/5\n"
        "🌐 Rasmiy veb-sayt: isft.uz"
    )
    await message.answer(text, parse_mode="HTML")
