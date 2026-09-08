# ISFT Instituti Yagona Aloqa Operatorlari Rahbari Boti

Ushbu bot faqat ISFT instituti Yagona aloqa operatorlari (Call-markaz, online chat, konsultatsiya) faoliyati yuzasidan talabalarning shikoyat, e'tiroz va takliflarini to'g'ridan-to'g'ri operatorlar rahbariga to'liq tugmalar orqali yetkazish uchun mo'ljallangan.

## Xususiyatlari
- **100% Tugmalar orqali boshqaruv:** Talaba har bir bosqichda inline va reply tugmalardan foydalanadi (Bo'lim tanlash, shikoyat sababi, qo'shimcha tafsilot, aloqa raqami).
- **Avtomatik tasdiq:** Murojaat yuborilgach, foydalanuvchiga:
  > **"Sizning murojaatingiz qabul qilindi, tegishli tartibda choralar ko'riladi"**
  xabari beriladi.
- **SQLite ma'lumotlar bazasi (`complaints.db`):** Har bir shikoyat tartib raqami, bo'limi, sababi, vaqti va holati bilan avtomatik saqlanadi.
- **Admin paneli:** Adminlar real vaqtda statistikani ko'rishi, murojaat holatini *"Ko'rib chiqilmoqda"* yoki *"Hal etildi"* ga o'zgartirishi mumkin.

---

## O'rnatish va Ishga Tushirish

1. Kutubxonalarni o'rnatish:
   ```bash
   pip install -r requirements.txt
   ```

2. `.env` faylida o'z Telegram ID raqamingizni kiriting (admin bildirishnomalari uchun):
   ```env
   BOT_TOKEN=8820246784:AAEA1jZltoiBBeeQUKpD4CjiOORm0Yuk-zE
   ADMIN_IDS=SIZNING_TELEGRAM_ID
   ```

3. Botni ishga tushirish:
   ```bash
   python main.py
   ```
