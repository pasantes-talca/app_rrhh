from pathlib import Path
import re
import uuid

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def safe_name(value: str) -> str:
    cleaned = _SAFE_NAME.sub("_", Path(value).name).strip("._")
    return cleaned[:180] or "archivo"


async def save_upload(upload: UploadFile, folder: str, allowed_types: frozenset[str]) -> str:
    if upload.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="unsupported_file_type")
    settings = get_settings()
    root = settings.upload_root.resolve()
    target_folder = (root / folder).resolve()
    if root not in target_folder.parents and target_folder != root:
        raise HTTPException(status_code=400, detail="invalid_storage_folder")
    target_folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{safe_name(upload.filename or 'archivo')}"
    target = target_folder / filename
    written = 0
    try:
        with target.open("xb") as destination:
            while chunk := await upload.read(1024 * 1024):
                written += len(chunk)
                if written > settings.max_upload_bytes:
                    raise HTTPException(status_code=413, detail="file_too_large")
                destination.write(chunk)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()
    return str(target.relative_to(root))


def resolve_private_path(relative_path: str) -> Path:
    root = get_settings().upload_root.resolve()
    target = (root / relative_path).resolve()
    if root in target.parents and target.is_file():
        return target
    # Legacy Flask rows sometimes stored paths prefixed with the upload folder
    # name (for example ``uploads/documentos_privados/x.pdf``). Accept that
    # representation only after normalising it back inside the configured root.
    parts = Path(relative_path).parts
    if parts and parts[0].lower() == root.name.lower():
        legacy_target = (root / Path(*parts[1:])).resolve()
        if root in legacy_target.parents and legacy_target.is_file():
            return legacy_target
    raise HTTPException(status_code=404, detail="file_not_found")
