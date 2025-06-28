from dotenv import load_dotenv
import os

# Завантажуємо змінні з .env
load_dotenv()

# Токен Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Шляхи
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
INTROS_DIR = os.path.join(MEDIA_DIR, 'intros')
OUTROS_DIR = os.path.join(MEDIA_DIR, 'outros')
OVERLAYS_DIR = os.path.join(MEDIA_DIR, 'overlays')

# Обмеження
MAX_VIDEO_SIZE_MB = 20          # максимум 20 MB для користувацьких відео
MAX_INTRO_DURATION_SEC = 10     # максимум 10 сек для інтро/аутро
MAX_VIDEO_NOTE_DURATION_SEC = 60  # максимум 60 сек для video_note
