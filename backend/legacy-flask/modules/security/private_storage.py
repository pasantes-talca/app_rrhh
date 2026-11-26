"""Almacenamiento local privado de prueba con autorización por propietario."""
import hashlib
import mimetypes
import os
import secrets
from dataclasses import dataclass
from pathlib import Path


ALLOWED = {
    "application/pdf": {".pdf"},
    "image/png": {".png"},
    "image/jpeg": {".jpg", ".jpeg"},
}
SIGNATURES = {
    "application/pdf": (b"%PDF-",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/jpeg": (b"\xff\xd8\xff",),
}


@dataclass(frozen=True)
class StoredDocument:
    internal_name: str
    original_name: str
    owner_id: int
    mime_type: str
    size: int
    sha256: str


class AntivirusScanner:
    def scan(self, content: bytes) -> bool:
        """Retorna True cuando el archivo es seguro."""
        raise NotImplementedError


class AllowAllTestScanner(AntivirusScanner):
    def scan(self, content: bytes) -> bool:
        return True


class PrivateStorage:
    def __init__(self, root, max_size=2 * 1024 * 1024, scanner=None):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.max_size = max_size
        self.scanner = scanner or AllowAllTestScanner()

    def store(self, owner_id: int, original_name: str, content: bytes, declared_mime: str):
        if not owner_id or not original_name:
            raise ValueError("missing_metadata")
        if len(content) > self.max_size:
            raise ValueError("file_too_large")
        suffix = Path(original_name).suffix.lower()
        if declared_mime not in ALLOWED or suffix not in ALLOWED[declared_mime]:
            raise ValueError("file_type_not_allowed")
        if not any(content.startswith(signature) for signature in SIGNATURES[declared_mime]):
            raise ValueError("mime_signature_mismatch")
        if not self.scanner.scan(content):
            raise ValueError("malware_detected")
        internal = secrets.token_hex(24) + suffix
        destination = (self.root / internal).resolve()
        if self.root not in destination.parents:
            raise ValueError("unsafe_path")
        destination.write_bytes(content)
        return StoredDocument(
            internal, os.path.basename(original_name), owner_id, declared_mime,
            len(content), hashlib.sha256(content).hexdigest(),
        )

    def read(self, document: StoredDocument, actor_id: int, privileged=False):
        if not privileged and actor_id != document.owner_id:
            raise PermissionError("document_access_denied")
        path = (self.root / document.internal_name).resolve()
        if self.root not in path.parents:
            raise PermissionError("unsafe_path")
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != document.sha256:
            raise ValueError("integrity_check_failed")
        return content

