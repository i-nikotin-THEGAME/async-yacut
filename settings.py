import os


class Config(object):
    """Основная конфигурация приложения"""

    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Максимальный размер файла 16MB
    DISK_TOKEN = os.getenv("DISK_TOKEN", "")
    BASE_URL = "http://localhost"
