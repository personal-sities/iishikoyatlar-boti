import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
import database
from handlers.complaint import router as complaint_router
from handlers.admin import admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Baza jadvallari tekshirilmoqda...")
    database.init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Routerni ro'yxatdan o'tkazish
    dp.include_router(admin_router)
    dp.include_router(complaint_router)
    
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username} ({bot_info.first_name})")
        
        # Eski kutilayotgan yangilanishlarni tozalab tashlash
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik yuz berdi: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
