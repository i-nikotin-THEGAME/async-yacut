from flask_wtf import FlaskForm
from wtforms import StringField, MultipleFileField
from wtforms.validators import DataRequired, URL, Length, Regexp, Optional
from flask_wtf.file import FileRequired


class URLForm(FlaskForm):
    """Форма для главной страницы - создание короткой ссылки"""

    original_link = StringField(
        "Длинная ссылка", validators=[DataRequired(message="Обязательное поле"), URL(message="Введите корректный URL")]
    )

    custom_id = StringField(
        "Ваш вариант короткой ссылки",
        validators=[
            Optional(),
            Length(max=16, message="Длина не более 16 символов"),
            Regexp(r"^[a-zA-Z0-9]+$", message="Используйте только латинские буквы и цифры"),
        ],
    )


class FileUploadForm(FlaskForm):
    """Форма для страницы загрузки файлов"""

    files = MultipleFileField("Файлы", validators=[FileRequired(message="Выберите хотя бы один файл для загрузки")])
