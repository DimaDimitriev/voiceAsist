"""Настройки ассистента. Секреты берутся из переменных окружения / файла .env (он в .gitignore)."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv необязателен: можно задать переменные в системе
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MAIL_USER = os.getenv("MAIL_USER", "")
MAIL_PASS = os.getenv("MAIL_PASS", "")  # для mail.ru — пароль для внешнего приложения
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.mail.ru")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_CITY = os.getenv("WEATHER_CITY", "Tomsk,RU")

# Путь к модели Vosk считается от папки проекта, а не от текущей папки терминала
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", os.path.join(BASE_DIR, "vosk-model-small-ru"))
