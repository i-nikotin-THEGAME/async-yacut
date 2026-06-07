from flask import render_template, redirect, url_for, flash
from yacut import app, db
from yacut.forms import URLForm, FileUploadForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id, check_unique_short_id
# from yacut.error_handlers import InvalidAPIUsage


@app.route("/", methods=["GET", "POST"])
def index_view():
    """Главная страница - создание короткой ссылки"""
    form = URLForm()

    if form.validate_on_submit():
        original_link = form.original_link.data
        custom_id = form.custom_id.data if form.custom_id.data else None

        # Проверка, что custom_id не равен 'files' (зарезервированный путь)
        if custom_id and custom_id.lower() == "files":
            flash("Предложенный вариант короткой ссылки уже существует", "danger")
            return render_template("index.html", form=form)

        # Если custom_id указан, проверяем его уникальность
        if custom_id:
            if not check_unique_short_id(custom_id):
                flash("Предложенный вариант короткой ссылки уже существует", "danger")
                return render_template("index.html", form=form)
            short_id = custom_id
        else:
            # Генерируем уникальный короткий идентификатор
            short_id = get_unique_short_id()

        # Создаем запись в базе данных
        url_map = URLMap()
        url_map.original = original_link
        url_map.short = short_id
        db.session.add(url_map)
        db.session.commit()

        short_url = f"{app.config['BASE_URL']}/{short_id}"
        flash(f"Ваша короткая ссылка: {short_url}", "success")
        return render_template("index.html", form=form, short_url=short_url)

    return render_template("index.html", form=form)


@app.route("/files", methods=["GET", "POST"])
def files_view():
    """Страница загрузки файлов на Яндекс Диск"""
    form = FileUploadForm()
    uploaded_files = []  # Список для хранения загруженных файлов и их ссылок

    if form.validate_on_submit():
        files = form.files.data

        # TODO: Здесь будет асинхронная загрузка на Яндекс Диск
        # Пока временная логика
        for file in files:
            # Генерируем короткую ссылку для файла
            short_id = get_unique_short_id()

            uploaded_files.append({
                'filename': file.filename,
                'short_link': f"{app.config['BASE_URL']}/{short_id}",
                'short_id': short_id
            })

            # Создаем запись в БД (нужно будет добавить тип ссылки)
            url_map = URLMap()
            url_map.original = f"file://{file.filename}"
            url_map.short = short_id
            db.session.add(url_map)

        db.session.commit()

        return render_template("files.html", form=form, uploaded_files=uploaded_files)

    return render_template("files.html", form=form, uploaded_files=uploaded_files)


@app.route("/<string:short_id>")
def redirect_to_original(short_id):
    """Переадресация по короткой ссылке"""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()

    # Если это файл (временно, пока не добавим поле type)
    if url_map.original.startswith("file://"):
        # TODO: Перенаправление на Яндекс Диск для скачивания
        return redirect(url_for("files_view"))

    return redirect(url_map.original)
