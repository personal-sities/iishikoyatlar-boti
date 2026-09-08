from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from config import ADMIN_IDS
import database
import keyboards

admin_router = Router()

# Admin panelga kirish
@admin_router.message(F.text.in_(["⚙️ Admin panel", "/admin"]))
async def open_admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        # Agar admin_ids bo'sh bo'lsa yoki admin bo'lmasa, birinchi bo'lib murojaat qilgan odamga ma'lumot beramiz
        if not ADMIN_IDS:
            await message.answer(
                f"⚠️ Hozirda hech qanday Admin ID sozlanmagan.\n"
                f"Sizning Telegram ID raqamingiz: <code>{message.from_user.id}</code>\n\n"
                f"Ushbu ID ni <code>.env</code> faylidagi <code>ADMIN_IDS</code> qatoriga qo'shishingiz mumkin.",
                parse_mode="HTML"
            )
            return
        await message.answer("⛔️ Sizda admin huquqlari mavjud emas.")
        return
        
    stats = database.get_statistics()
    text = (
        "⚙️ <b>ISFT Instituti Yagona aloqa operatorlari rahbarining boti — Admin Paneli</b>\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"• Jami murojaatlar: <b>{stats['total']}</b>\n"
        f"• Yangi: <b>{stats['new']}</b> ta\n"
        f"• Ko'rib chiqilmoqda: <b>{stats['in_review']}</b> ta\n"
        f"• Hal etilgan: <b>{stats['resolved']}</b> ta\n"
        f"• Foydalanuvchilar: <b>{stats['total_users']}</b> ta"
    )
    await message.answer(text, reply_markup=keyboards.get_admin_kb(), parse_mode="HTML")

# Admin statistika
@admin_router.callback_query(F.data == "admin_stats")
async def show_admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
        
    stats = database.get_statistics()
    text = (
        "📊 <b>Murojaatlar statistikasi:</b>\n\n"
        f"📁 Jami qabul qilingan: <b>{stats['total']}</b>\n"
        f"🆕 Yangi (ko'rilmagan): <b>{stats['new']}</b>\n"
        f"⏳ O'rganilmoqda: <b>{stats['in_review']}</b>\n"
        f"✅ Ijobiy hal etilgan: <b>{stats['resolved']}</b>\n"
        f"👥 Foydalanuvchilar soni: <b>{stats['total_users']}</b>"
    )
    await callback.message.edit_text(text, reply_markup=keyboards.get_admin_kb(), parse_mode="HTML")
    await callback.answer()

# Yangi shikoyatlar ro'yxati
@admin_router.callback_query(F.data.in_(["admin_new_complaints", "admin_recent_complaints"]))
async def show_complaints_list(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
        
    status_filter = "Yangi" if callback.data == "admin_new_complaints" else None
    complaints = database.get_recent_complaints(limit=5, status=status_filter)
    
    if not complaints:
        await callback.answer("Hozircha murojaatlar mavjud emas.", show_alert=True)
        return
        
    for c in complaints:
        if len(c) == 11:
            c_id, u_id, name, username, phone, dept, reason, details, student_id, status, dt = c
        else:
            c_id, u_id, name, username, phone, dept, reason, details, status, dt = c
            student_id = "—"
        card = (
            f"📋 <b>Murojaat #{c_id}</b> [{status}]\n"
            f"👤 <b>Talaba:</b> {name} (@{username if username else 'yo‘q'})\n"
            f"🎓 <b>Talabalik ID:</b> <code>{student_id}</code>\n"
            f"📞 <b>Bog'lanilgan raqam:</b> {phone}\n"
            f"🏛 <b>Operator:</b> {dept}\n"
            f"⚠️ <b>Sabab:</b> {reason}\n"
            f"📝 <b>Tafsilot:</b> {details}\n"
            f"⏰ <b>Vaqt:</b> {dt}"
        )
        await callback.message.answer(
            card, 
            reply_markup=keyboards.get_complaint_action_kb(c_id),
            parse_mode="HTML"
        )
        
    await callback.answer()

# Holatni o'zgartirish
@admin_router.callback_query(F.data.startswith("status_"))
async def change_status_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return
        
    parts = callback.data.split("_")
    complaint_id = int(parts[1])
    action = parts[2]
    
    new_status = "Ko‘rib chiqilmoqda" if action == "review" else "Hal etildi"
    database.update_status(complaint_id, new_status)
    
    await callback.answer(f"#{complaint_id} statusi «{new_status}»ga o'zgartirildi!")
    
    # Xabarni yangilash
    c = database.get_complaint(complaint_id)
    if c:
        if len(c) == 11:
            c_id, u_id, name, username, phone, dept, reason, details, student_id, status, dt = c
        else:
            c_id, u_id, name, username, phone, dept, reason, details, status, dt = c
            student_id = "—"
        card = (
            f"📋 <b>Murojaat #{c_id}</b> [<b>{status}</b>]\n"
            f"👤 <b>Talaba:</b> {name} (@{username if username else 'yo‘q'})\n"
            f"🎓 <b>Talabalik ID:</b> <code>{student_id}</code>\n"
            f"📞 <b>Bog'lanilgan raqam:</b> {phone}\n"
            f"🏛 <b>Operator:</b> {dept}\n"
            f"⚠️ <b>Sabab:</b> {reason}\n"
            f"📝 <b>Tafsilot:</b> {details}\n"
            f"⏰ <b>Vaqt:</b> {dt}"
        )
        await callback.message.edit_text(
            card,
            reply_markup=keyboards.get_complaint_action_kb(c_id),
            parse_mode="HTML"
        )

# Admin panelni yopish
@admin_router.callback_query(F.data == "admin_close")
async def close_admin_panel(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Admin panel yopildi.")
