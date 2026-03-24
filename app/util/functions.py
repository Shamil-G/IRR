import json
import os
import re
from datetime import datetime
from fastapi import Request, UploadFile
from app.core.logger import log
from app.util.regions import regions
from app.config.app_config import UPLOAD_DIR


def get_regions(top_view: int, rfbn_id: str) -> dict:
    if top_view == 0:
        # Возвращаем только регион пользователя
        return { rfbn_id: regions[rfbn_id] }
    else:
        # Возвращаем все регионы
        return regions


async def extract_payload(request: Request) -> dict:
    """
    Универсальный парсер входящих данных.
    Поддерживает:
    - GET параметры
    - JSON body
    - form-urlencoded
    - попытку ручного JSON-декодирования
    """

    # -----------------------------
    # GET
    # -----------------------------
    if request.method == "GET":
        return dict(request.query_params)

    # -----------------------------
    # Content-Type
    # -----------------------------
    content_type = request.headers.get("content-type", "")
    log.info(f"📥 Content-Type: {content_type}")

    # -----------------------------
    # JSON
    # -----------------------------
    if "application/json" in content_type:
        try:
            return await request.json()
        except Exception as e:
            log.info(f"⚠️ JSON не распарсен: {e}, пробуем вручную")
            try:
                raw = await request.body()
                return json.loads(raw.decode("utf-8"))
            except Exception as e2:
                log.info(f"❌ Ошибка ручного JSON-декодирования: {e2}")
                return {}

    # -----------------------------
    # form-urlencoded
    # -----------------------------
    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        return dict(form)

    # -----------------------------
    # fallback: пробуем JSON вручную
    # -----------------------------
    try:
        raw = await request.body()
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}


def sanitize_filename(name: str) -> str:
    """
    Разрешаем кириллицу, латиницу, цифры, пробелы, дефис, подчёркивание, точку.
    """
    name = re.sub(r"[^0-9A-Za-zА-Яа-яЁё ._-]", "", name)
    return name.strip()


async def upload_files(rfbn_id: str, files: list[UploadFile]):
    """
    Сохранение файлов из FastAPI UploadFile.
    """
    yr = datetime.now().year
    upload_path = f"{UPLOAD_DIR}/{yr}/{rfbn_id}"

    os.makedirs(upload_path, exist_ok=True)

    saved_paths = []

    for f in files:
        if not f.filename:
            continue

        filename = sanitize_filename(f.filename)
        path = os.path.join(upload_path, filename)

        # FastAPI UploadFile → f.read()
        with open(path, "wb") as out:
            out.write(await f.read())

        saved_paths.append(path)

    return saved_paths


def flash(request, message, category="message"):
    flashes = request.session.get("_flashes", [])
    flashes.append((category, message))
    request.session["_flashes"] = flashes


def get_flashed_messages(request, with_categories=False):
    flashes = request.session.pop("_flashes", [])

    if with_categories:
        return flashes

    return [msg for _, msg in flashes]
