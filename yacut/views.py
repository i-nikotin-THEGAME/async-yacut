import asyncio
from flask import render_template, redirect, flash
from yacut import app, db
from yacut.constants import RESERVED_SHORT_IDS
from yacut.forms import URLForm, FileUploadForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id, check_unique_short_id
from yacut.yandex_disk import YandexDiskClient


@app.route("/", methods=["GET", "POST"])
def index_view():
    """Главная страница - создание короткой ссылки"""
    form = URLForm()

    if form.validate_on_submit():
        original_link = form.original_link.data
        custom_id = form.custom_id.data if form.custom_id.data else None

        if custom_id and custom_id.lower() in RESERVED_SHORT_IDS:
            flash(
                "Предложенный вариант короткой ссылки уже существует.",
                "danger"
            )
            return render_template("index.html", form=form)

        if custom_id:
            if not check_unique_short_id(custom_id):
                flash(
                    "Предложенный вариант короткой ссылки уже существует.",
                    "danger"
                )
                return render_template("index.html", form=form)
            short_id = custom_id
        else:
            short_id = get_unique_short_id()

        url_map = URLMap()
        url_map.original = original_link
        url_map.short = short_id
        db.session.add(url_map)
        db.session.commit()

        short_url = f"{app.config['BASE_URL']}/{short_id}"
        flash(f"Ваша короткая ссылка: {short_url}", "success")
        return render_template("index.html", form=form, short_url=short_url)

    return render_template("index.html", form=form)


async def process_file_upload(file, disk_client):
    """Асинхронная обработка одного файла"""
    file_content = file.read()
    try:
        public_link = await disk_client.upload_and_share(
            file_content,
            file.filename
        )
        return (file, public_link, None)
    except Exception as e:
        return (file, None, str(e))


async def upload_all_files_async(files, disk_client):
    """Загружает все файлы асинхронно и возвращает результаты"""
    tasks = [process_file_upload(file, disk_client) for file in files]
    return await asyncio.gather(*tasks)


def save_uploaded_files(upload_results, app_config, db_session):
    """Сохраняет результаты загрузки в БД"""
    uploaded_files = []
    for result in upload_results:
        file, public_link, error = result
        if error:
            uploaded_files.append({"filename": file.filename, "error": error})
        elif public_link:
            short_id = get_unique_short_id()
            uploaded_files.append(
                {
                    "filename": file.filename,
                    "short_link": f"{app_config['BASE_URL']}/{short_id}",
                    "short_id": short_id,
                }
            )
            url_map = URLMap()
            url_map.original = public_link
            url_map.short = short_id
            db_session.add(url_map)
        else:
            uploaded_files.append({
                "filename": file.filename,
                "error": "Ошибка загрузки"
            })

    db_session.commit()
    return uploaded_files


@app.route("/files", methods=["GET", "POST"])
def files_view():
    """Страница загрузки файлов на Яндекс Диск"""
    form = FileUploadForm()
    uploaded_files = []

    if form.validate_on_submit():
        files = form.files.data

        if not app.config.get("DISK_TOKEN"):
            flash("Не настроен токен Яндекс Диска", "danger")
            return render_template(
                "files.html",
                form=form,
                uploaded_files=uploaded_files
            )

        disk_client = YandexDiskClient(app.config["DISK_TOKEN"])

        upload_results = asyncio.run(
            upload_all_files_async(files, disk_client)
        )
        uploaded_files = save_uploaded_files(
            upload_results,
            app.config,
            db.session
        )

        success_count = len([f for f in uploaded_files if "error" not in f])
        flash(f"Загружено {success_count} файлов", "success")

        return render_template(
            "files.html", form=form, uploaded_files=uploaded_files
        )

    return render_template(
        "files.html",
        form=form,
        uploaded_files=uploaded_files
    )


@app.route("/<string:short_id>")
def redirect_to_original(short_id):
    """Переадресация по короткой ссылке"""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
