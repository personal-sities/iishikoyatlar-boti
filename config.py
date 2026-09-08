import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8820246784:AAEA1jZltoiBBeeQUKpD4CjiOORm0Yuk-zE")
DB_NAME = os.getenv("DB_NAME", "complaints.db")

# Admin Telegram IDlari (Murojaatlar yuboriladigan chat ID)
admin_ids_raw = os.getenv("ADMIN_IDS", "5473259177")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in admin_ids_raw.split(",") if admin_id.strip().isdigit()]
if 5473259177 not in ADMIN_IDS:
    ADMIN_IDS.append(5473259177)
