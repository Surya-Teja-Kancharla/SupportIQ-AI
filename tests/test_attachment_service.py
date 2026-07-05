from pathlib import Path

import pytest

import app.services.attachment_service as attachment_service
from app.services.attachment_service import sanitize_filename, save_attachment


def test_sanitize_filename_removes_directory_traversal():
    filename = "../../secret/report.pdf"

    result = sanitize_filename(filename)

    assert result == "report.pdf"


def test_sanitize_filename_replaces_unsafe_characters():
    filename = "customer error screenshot (final)@2026!.png"

    result = sanitize_filename(filename)

    assert result == "customer_error_screenshot__final__2026_.png"


def test_sanitize_filename_preserves_safe_characters():
    filename = "error-report_2026.07.05.pdf"

    result = sanitize_filename(filename)

    assert result == "error-report_2026.07.05.pdf"


def test_save_attachment_accepts_allowed_extension(tmp_path, monkeypatch):
    monkeypatch.setattr(
        attachment_service,
        "ATTACHMENT_DIRECTORY",
        tmp_path,
    )

    content = b"sample pdf content"

    result = save_attachment(
        filename="report.pdf",
        content=content,
        content_type="application/pdf",
    )

    assert result is not None
    assert result.original_filename == "report.pdf"
    assert result.stored_filename.endswith("_report.pdf")
    assert result.content_type == "application/pdf"
    assert result.size_bytes == len(content)

    stored_file = Path(result.file_path)

    assert stored_file.exists()
    assert stored_file.read_bytes() == content


def test_save_attachment_rejects_disallowed_extension(tmp_path, monkeypatch):
    monkeypatch.setattr(
        attachment_service,
        "ATTACHMENT_DIRECTORY",
        tmp_path,
    )

    result = save_attachment(
        filename="malware.exe",
        content=b"dangerous executable",
        content_type="application/octet-stream",
    )

    assert result is None
    assert list(tmp_path.iterdir()) == []


def test_save_attachment_rejects_filename_without_extension(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        attachment_service,
        "ATTACHMENT_DIRECTORY",
        tmp_path,
    )

    result = save_attachment(
        filename="README",
        content=b"no extension",
        content_type="text/plain",
    )

    assert result is None
    assert list(tmp_path.iterdir()) == []


def test_save_attachment_rejects_oversized_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        attachment_service,
        "ATTACHMENT_DIRECTORY",
        tmp_path,
    )

    monkeypatch.setattr(
        attachment_service.settings,
        "max_attachment_size_mb",
        1,
    )

    oversized_content = b"x" * ((1024 * 1024) + 1)

    result = save_attachment(
        filename="large.pdf",
        content=oversized_content,
        content_type="application/pdf",
    )

    assert result is None
    assert list(tmp_path.iterdir()) == []


def test_save_attachment_generates_unique_filenames(tmp_path, monkeypatch):
    monkeypatch.setattr(
        attachment_service,
        "ATTACHMENT_DIRECTORY",
        tmp_path,
    )

    first_result = save_attachment(
        filename="error.png",
        content=b"first",
        content_type="image/png",
    )

    second_result = save_attachment(
        filename="error.png",
        content=b"second",
        content_type="image/png",
    )

    assert first_result is not None
    assert second_result is not None

    assert first_result.stored_filename != second_result.stored_filename

    assert len(list(tmp_path.iterdir())) == 2
