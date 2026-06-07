from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from yacut.settings import Config
from dotenv import load_dotenv


# Загружаем переменные окружения из .env файла
load_dotenv(override=True)

# Создаем приложение
app = Flask(__name__, static_folder="static")

# Загружаем конфигурацию
app.config.from_object(Config)
app.json.ensure_ascii = False

# Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from yacut import views, api_views, error_handlers
