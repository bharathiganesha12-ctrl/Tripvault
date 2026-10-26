"""
TripVault – Document storage service
Phase 2: saves encrypted files locally under storage/encrypted/
Phase 3: will swap local storage for AWS S3
"""

import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename

from database.extensions import db
from database.models import Document

# Local storage directory
STORAGE_DIR = Path(__file__).parent.parent / 'storage' / 'encrypted'
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_BYTES = 25 * 1024 * 1024  # 25 MB


def _encrypt_bytes(data: bytes, key: bytes) -> bytes:
    """
    AES-256-CBC encryption using the cryptography library.
    Returns iv (16 bytes) + ciphertext.
    """
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    import os as _os

    iv         = _os.urandom(16)
    # Pad to 16-byte boundary (PKCS7 manual)
    pad_len    = 16 - (len(data) % 16)
    padded     = data + bytes([pad_len] * pad_len)
    cipher     = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor  = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return iv + ciphertext


def _decrypt_bytes(data: bytes, key: bytes) -> bytes:
    """Decrypt iv+ciphertext produced by _encrypt_bytes."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    iv         = data[:16]
    ciphertext = data[16:]
    cipher     = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor  = cipher.decryptor()
    padded     = decryptor.update(ciphertext) + decryptor.finalize()
    pad_len    = padded[-1]
    return padded[:-pad_len]


def _get_enc_key() -> bytes:
    """
    Return a 32-byte AES key from env var ENCRYPTION_KEY.
    Falls back to a deterministic dev key (NOT for production).
    """
    raw = os.environ.get('ENCRYPTION_KEY', 'dev-tripvault-key-change-me-32byt')
    key = raw.encode('utf-8')[:32].ljust(32, b'\x00')
    return key


def save_document(user_id: int, file_storage, doc_type: str,
                  display_name: str) -> Document:
    """
    Encrypt and save an uploaded FileStorage object.
    Returns the persisted Document model instance.
    """
    raw_bytes = file_storage.read()

    if len(raw_bytes) > MAX_FILE_BYTES:
        raise ValueError('File exceeds the 25 MB limit.')

    key          = _get_enc_key()
    encrypted    = _encrypt_bytes(raw_bytes, key)
    safe_name    = secure_filename(file_storage.filename)
    unique_name  = f'{uuid.uuid4().hex}_{safe_name}.enc'
    dest_path    = STORAGE_DIR / unique_name

    with open(dest_path, 'wb') as f:
        f.write(encrypted)

    doc = Document(
        user_id       = user_id,
        doc_type      = doc_type,
        display_name  = display_name.strip() or safe_name,
        original_name = safe_name,
        file_size     = len(raw_bytes),
        mime_type     = file_storage.mimetype,
        local_path    = str(dest_path),
        storage_key   = None,       # populated in Phase 3 (S3)
        is_encrypted  = True,
    )
    db.session.add(doc)
    db.session.commit()
    return doc


def get_document_bytes(doc: Document) -> bytes:
    """Decrypt and return raw file bytes for download."""
    if not doc.local_path or not Path(doc.local_path).exists():
        raise FileNotFoundError('Document file not found on server.')
    key = _get_enc_key()
    with open(doc.local_path, 'rb') as f:
        encrypted = f.read()
    return _decrypt_bytes(encrypted, key)


def delete_document(doc: Document) -> None:
    """Remove encrypted file and DB record."""
    if doc.local_path:
        try:
            Path(doc.local_path).unlink(missing_ok=True)
        except Exception:
            pass
    db.session.delete(doc)
    db.session.commit()


def get_user_documents(user_id: int):
    return (Document.query
            .filter_by(user_id=user_id)
            .order_by(Document.uploaded_at.desc())
            .all())


def get_storage_stats(user_id: int) -> dict:
    """Return storage stats for a user."""
    docs = get_user_documents(user_id)
    total_bytes = sum(d.file_size for d in docs)
    used_mb = round(total_bytes / 1_048_576, 2)
    quota_mb = 5 * 1024   # 5 GB in MB
    pct = min(round(used_mb / quota_mb * 100, 1), 100)
    return {
        'total_bytes': total_bytes,
        'used_mb':     used_mb,
        'quota_mb':    quota_mb,
        'pct':         pct,
        'count':       len(docs),
    }
