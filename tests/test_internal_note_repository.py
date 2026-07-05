from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.models.internal_note import InternalNote
from app.repositories.internal_note_repository import InternalNoteRepository


def test_create_internal_note():
    db = MagicMock()

    repository = InternalNoteRepository()

    created_note = repository.create(
        db,
        ticket_id=1,
        note="Customer requested an update.",
        created_by="support-agent",
    )

    assert isinstance(created_note, InternalNote)

    assert created_note.ticket_id == 1
    assert created_note.note == "Customer requested an update."
    assert created_note.created_by == "support-agent"

    db.add.assert_called_once_with(created_note)
    db.flush.assert_called_once()
    db.refresh.assert_called_once_with(created_note)

    db.commit.assert_not_called()


def test_list_internal_notes_by_ticket():
    db = MagicMock()

    repository = InternalNoteRepository()

    newest_note = InternalNote(
        id=2,
        ticket_id=1,
        note="Newest internal note",
        created_by="agent-2",
        created_at=datetime(
            2026,
            7,
            5,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )

    older_note = InternalNote(
        id=1,
        ticket_id=1,
        note="Older internal note",
        created_by="agent-1",
        created_at=datetime(
            2026,
            7,
            5,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    scalar_result = MagicMock()
    scalar_result.all.return_value = [
        newest_note,
        older_note,
    ]

    db.scalars.return_value = scalar_result

    result = repository.list_by_ticket(
        db,
        ticket_id=1,
    )

    assert result == [
        newest_note,
        older_note,
    ]

    db.scalars.assert_called_once()


def test_list_internal_notes_returns_empty_list():
    db = MagicMock()

    repository = InternalNoteRepository()

    scalar_result = MagicMock()
    scalar_result.all.return_value = []

    db.scalars.return_value = scalar_result

    result = repository.list_by_ticket(
        db,
        ticket_id=999,
    )

    assert result == []

    db.scalars.assert_called_once()
