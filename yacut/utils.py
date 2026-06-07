import random
import string
from yacut.models import URLMap


def get_unique_short_id(length=6):
    """
    Генерирует уникальный короткий идентификатор.
    """
    # Допустимые символы: латиница (верхний и нижний регистр) + цифры
    characters = string.ascii_letters + string.digits

    while True:
        # Генерируем случайный идентификатор
        short_id = "".join(random.choice(characters) for _ in range(length))

        # Проверяем уникальность в базе данных
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id


def check_unique_short_id(short_id):
    """
    Проверяет, существует ли уже такой короткий идентификатор.
    """
    return URLMap.query.filter_by(short=short_id).first() is None
