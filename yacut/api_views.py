import re

from flask import request, jsonify, Blueprint
from yacut import db
from yacut.constants import (
    RESERVED_SHORT_IDS,
    SHORT_ID_MAX_LEN,
    SHORT_ID_PATTERN,
)
from yacut.models import URLMap
from yacut.utils import get_unique_short_id, check_unique_short_id
from yacut.error_handlers import InvalidAPIUsage

bp = Blueprint("api", __name__)


@bp.route("/id/", methods=["POST"])
def create_short_link():
    """
    POST /api/id/
    Создание новой короткой ссылки
    """

    # Проверяем наличие тела запроса ДО вызова get_json
    if request.content_length == 0 or request.data == b"":
        raise InvalidAPIUsage("Отсутствует тело запроса")

    data = request.get_json()

    # Проверка: есть ли тело запроса
    if data is None:
        raise InvalidAPIUsage("Отсутствует тело запроса")

    # Проверка: есть ли поле url
    if "url" not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    original_url = data["url"]
    custom_id = data.get("custom_id")

    # Проверка: если custom_id указан и равен 'files'
    if custom_id and custom_id.lower() in RESERVED_SHORT_IDS:
        raise InvalidAPIUsage(
            "Предложенный вариант короткой ссылки уже существует."
        )

    # Если custom_id указан
    if custom_id:
        # Проверка валидности custom_id (только латиница и цифры, длина до 16)
        is_valid_format = re.match(SHORT_ID_PATTERN, custom_id)
        is_valid_length = len(custom_id) <= SHORT_ID_MAX_LEN

        if not is_valid_format or not is_valid_length:
            raise InvalidAPIUsage(
                "Указано недопустимое имя для короткой ссылки"
            )

        # Проверка уникальности
        if not check_unique_short_id(custom_id):
            raise InvalidAPIUsage(
                "Предложенный вариант короткой ссылки уже существует."
            )

        short_id = custom_id
    else:
        # Генерируем уникальный короткий идентификатор
        short_id = get_unique_short_id()

    # Создаем запись в БД
    url_map = URLMap()
    url_map.original = original_url
    url_map.short = short_id
    db.session.add(url_map)
    db.session.commit()

    return jsonify(url_map.to_dict()), 201


@bp.route("/id/<string:short_id>/", methods=["GET"])
def get_original_link(short_id):
    """
    GET /api/id/<short_id>/
    Получение оригинальной ссылки по короткому идентификатору
    """
    url_map = URLMap.query.filter_by(short=short_id).first()

    if url_map is None:
        raise InvalidAPIUsage("Указанный id не найден", status_code=404)

    return jsonify({"url": url_map.original}), 200
