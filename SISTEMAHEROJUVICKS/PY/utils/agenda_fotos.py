import base64
import json
import os
import shutil
import uuid
from datetime import datetime

from database import DATA_DIR


PHOTO_PREFIX = "ARQUIVO_LOCAL:"
PHOTO_ROOT = "AGENDA_FOTOS"
PHOTO_EXT_BY_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
}


def carregar_lista_fotos(raw_value):
    if raw_value in (None, "", "null"):
        return []

    if isinstance(raw_value, list):
        return [item for item in raw_value if item]

    try:
        data = json.loads(raw_value)
    except (TypeError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []
    return [item for item in data if item]


def eh_referencia_local(item):
    return isinstance(item, str) and item.startswith(PHOTO_PREFIX)


def _orcamento_photo_dir(orc_id):
    dir_path = os.path.join(DATA_DIR, PHOTO_ROOT, f"orcamento_{int(orc_id)}")
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def _resolve_local_path(item):
    if not eh_referencia_local(item):
        return None
    relative_path = item[len(PHOTO_PREFIX):].replace("/", os.sep)
    return os.path.normpath(os.path.join(DATA_DIR, relative_path))


def _bytes_para_referencia_local(orc_id, img_bytes, original_name="", mime_type=""):
    if not img_bytes:
        return None

    ext = os.path.splitext(original_name or "")[1].lower()
    if not ext:
        ext = PHOTO_EXT_BY_MIME.get(mime_type, ".img")

    file_name = f"{datetime.now():%Y%m%d_%H%M%S_%f}_{uuid.uuid4().hex[:8]}{ext}"
    abs_path = os.path.join(_orcamento_photo_dir(orc_id), file_name)

    with open(abs_path, "wb") as file_handle:
        file_handle.write(img_bytes)

    relative_path = os.path.relpath(abs_path, DATA_DIR).replace("\\", "/")
    return f"{PHOTO_PREFIX}{relative_path}"


def foto_para_bytes(item):
    if not item:
        return None

    if eh_referencia_local(item):
        abs_path = _resolve_local_path(item)
        if not abs_path or not os.path.exists(abs_path):
            return None
        with open(abs_path, "rb") as file_handle:
            return file_handle.read()

    if isinstance(item, str):
        try:
            return base64.b64decode(item)
        except Exception:
            return None

    return None


def foto_para_base64(item):
    if not item:
        return None

    if eh_referencia_local(item):
        img_bytes = foto_para_bytes(item)
        if not img_bytes:
            return None
        return base64.b64encode(img_bytes).decode()

    if isinstance(item, str):
        try:
            base64.b64decode(item)
            return item
        except Exception:
            return None

    return None


def salvar_fotos_uploads(orc_id, uploaded_files, fotos_existentes=None):
    fotos = list(fotos_existentes or [])
    for uploaded in uploaded_files or []:
        img_bytes = uploaded.getvalue()
        if not img_bytes:
            continue
        foto_ref = _bytes_para_referencia_local(
            orc_id,
            img_bytes,
            getattr(uploaded, "name", ""),
            getattr(uploaded, "type", "")
        )
        if foto_ref:
            fotos.append(foto_ref)
    return fotos


def normalizar_fotos_para_armazenar(lista_fotos, orc_id):
    fotos_normalizadas = []
    for item in lista_fotos or []:
        if eh_referencia_local(item):
            abs_path = _resolve_local_path(item)
            if abs_path and os.path.exists(abs_path):
                fotos_normalizadas.append(item)
            continue

        img_bytes = foto_para_bytes(item)
        if not img_bytes:
            continue

        foto_ref = _bytes_para_referencia_local(orc_id, img_bytes)
        if foto_ref:
            fotos_normalizadas.append(foto_ref)

    return fotos_normalizadas


def remover_foto_da_lista(lista_fotos, idx):
    fotos = list(lista_fotos or [])
    if idx < 0 or idx >= len(fotos):
        return fotos

    item = fotos.pop(idx)
    if eh_referencia_local(item):
        abs_path = _resolve_local_path(item)
        if abs_path and os.path.exists(abs_path):
            try:
                os.remove(abs_path)
            except OSError:
                pass
        parent_dir = os.path.dirname(abs_path) if abs_path else ""
        if parent_dir and os.path.isdir(parent_dir) and not os.listdir(parent_dir):
            try:
                os.rmdir(parent_dir)
            except OSError:
                pass

    return fotos


def limpar_fotos_orcamento(orc_id):
    try:
        dir_path = os.path.join(DATA_DIR, PHOTO_ROOT, f"orcamento_{int(orc_id)}")
    except (TypeError, ValueError):
        return

    if os.path.isdir(dir_path):
        try:
            shutil.rmtree(dir_path)
        except OSError:
            pass
