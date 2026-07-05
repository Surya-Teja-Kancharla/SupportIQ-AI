import re
import uuid
from pathlib import Path

from app.config.settings import settings
from app.schemas.email_schema import ParsedAttachment


ATTACHMENT_DIRECTORY = Path("uploads/attachments")


def sanitize_filename(filename: str) -> str:
    filename = Path(filename).name

    filename = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        filename,
    )

    return filename


def save_attachment(
    filename: str,
    content: bytes,
    content_type: str | None = None,
) -> ParsedAttachment | None:

    safe_filename = sanitize_filename(filename)

    extension = Path(safe_filename).suffix.lower().lstrip(".")

    if not extension:
        return None

    if extension not in settings.allowed_attachment_extensions:
        return None

    maximum_size_bytes = (
        settings.max_attachment_size_mb
        * 1024
        * 1024
    )

    if len(content) > maximum_size_bytes:
        return None

    ATTACHMENT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = (
        f"{uuid.uuid4().hex}_{safe_filename}"
    )

    file_path = (
        ATTACHMENT_DIRECTORY
        / stored_filename
    )

    file_path.write_bytes(content)

    return ParsedAttachment(
        original_filename=filename,
        stored_filename=stored_filename,
        file_path=str(file_path),
        content_type=content_type,
        size_bytes=len(content),
    )
