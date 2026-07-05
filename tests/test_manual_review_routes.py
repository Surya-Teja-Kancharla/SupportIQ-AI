from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_db
from app.api.manual_review_routes import (
    manual_review_service,
    router,
)


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def app(db):
    test_app = FastAPI()

    test_app.include_router(router)

    def override_get_db():
        yield db

    test_app.dependency_overrides[get_db] = override_get_db

    return test_app


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_manual_review_service_mock():
    manual_review_service.update_category = MagicMock()
    manual_review_service.update_priority = MagicMock()
    manual_review_service.reassign_team = MagicMock()
    manual_review_service.update_status = MagicMock()
    manual_review_service.add_internal_note = MagicMock()
    manual_review_service.edit_suggested_reply = MagicMock()
    manual_review_service.regenerate_suggested_reply = MagicMock()

    yield


def test_update_category_route(client):
    manual_review_service.update_category.return_value = SimpleNamespace(
        id=1,
        category="Account Access",
    )

    response = client.post(
        "/tickets/1/category",
        json={
            "category": "Account Access",
            "performed_by": "support-agent",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "ticket_id": 1,
        "category": "Account Access",
    }

    manual_review_service.update_category.assert_called_once()

    call_args = (
        manual_review_service
        .update_category
        .call_args
    )

    assert call_args.kwargs["ticket_id"] == 1
    assert call_args.kwargs["category"] == "Account Access"
    assert call_args.kwargs["performed_by"] == "support-agent"


def test_update_priority_route(client):
    manual_review_service.update_priority.return_value = SimpleNamespace(
        id=1,
        priority="HIGH",
    )

    response = client.post(
        "/tickets/1/priority",
        json={
            "priority": "HIGH",
            "performed_by": "support-agent",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "ticket_id": 1,
        "priority": "HIGH",
    }


def test_reassign_team_route(client):
    manual_review_service.reassign_team.return_value = SimpleNamespace(
        id=1,
        assigned_team="Billing Support",
    )

    response = client.post(
        "/tickets/1/team",
        json={
            "assigned_team": "Billing Support",
            "performed_by": "support-agent",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "ticket_id": 1,
        "assigned_team": "Billing Support",
    }


def test_update_status_route(client):
    manual_review_service.update_status.return_value = SimpleNamespace(
        id=1,
        status="IN_PROGRESS",
    )

    response = client.post(
        "/tickets/1/status",
        json={
            "status": "IN_PROGRESS",
            "performed_by": "support-agent",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "ticket_id": 1,
        "status": "IN_PROGRESS",
    }


def test_add_internal_note_route(client):
    manual_review_service.add_internal_note.return_value = SimpleNamespace(
        id=10,
        ticket_id=1,
        note="Waiting for customer confirmation.",
        created_by="support-agent",
        created_at="2026-07-05T12:00:00+00:00",
    )

    response = client.post(
        "/tickets/1/notes",
        json={
            "note": "Waiting for customer confirmation.",
            "created_by": "support-agent",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 10,
        "ticket_id": 1,
        "note": "Waiting for customer confirmation.",
        "created_by": "support-agent",
        "created_at": "2026-07-05T12:00:00+00:00",
    }


def test_edit_suggested_reply_route(client):
    manual_review_service.edit_suggested_reply.return_value = (
        SimpleNamespace(
            id=1,
            suggested_reply="Edited support response.",
        )
    )

    response = client.post(
        "/tickets/1/suggested-reply",
        json={
            "suggested_reply": "Edited support response.",
            "performed_by": "support-agent",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "ticket_id": 1,
        "suggested_reply": "Edited support response.",
    }


def test_regenerate_suggested_reply_route(client):
    manual_review_service.regenerate_suggested_reply.return_value = (
        SimpleNamespace(
            id=1,
            suggested_reply="Regenerated AI reply.",
        )
    )

    response = client.post(
        "/tickets/1/suggested-reply/regenerate",
        json={
            "performed_by": "support-agent",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "ticket_id": 1,
        "suggested_reply": "Regenerated AI reply.",
    }


@pytest.mark.parametrize(
    ("endpoint", "payload", "service_method"),
    [
        (
            "/tickets/999/category",
            {
                "category": "Billing",
                "performed_by": "support-agent",
            },
            "update_category",
        ),
        (
            "/tickets/999/priority",
            {
                "priority": "HIGH",
                "performed_by": "support-agent",
            },
            "update_priority",
        ),
        (
            "/tickets/999/team",
            {
                "assigned_team": "Billing Support",
                "performed_by": "support-agent",
            },
            "reassign_team",
        ),
        (
            "/tickets/999/status",
            {
                "status": "CLOSED",
                "performed_by": "support-agent",
            },
            "update_status",
        ),
        (
            "/tickets/999/notes",
            {
                "note": "Test note",
                "created_by": "support-agent",
            },
            "add_internal_note",
        ),
        (
            "/tickets/999/suggested-reply",
            {
                "suggested_reply": "Edited reply",
                "performed_by": "support-agent",
            },
            "edit_suggested_reply",
        ),
        (
            "/tickets/999/suggested-reply/regenerate",
            {
                "performed_by": "support-agent",
            },
            "regenerate_suggested_reply",
        ),
    ],
)
def test_manual_review_routes_return_404_for_missing_ticket(
    client,
    endpoint,
    payload,
    service_method,
):
    mocked_method = getattr(
        manual_review_service,
        service_method,
    )

    mocked_method.side_effect = ValueError(
        "Ticket 999 not found"
    )

    response = client.post(
        endpoint,
        json=payload,
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Ticket 999 not found",
    }


def test_category_route_rejects_empty_category(client):
    response = client.post(
        "/tickets/1/category",
        json={
            "category": "",
            "performed_by": "support-agent",
        },
    )

    assert response.status_code == 422

    manual_review_service.update_category.assert_not_called()


def test_note_route_rejects_empty_note(client):
    response = client.post(
        "/tickets/1/notes",
        json={
            "note": "",
            "created_by": "support-agent",
        },
    )

    assert response.status_code == 422

    manual_review_service.add_internal_note.assert_not_called()


def test_suggested_reply_route_rejects_empty_reply(client):
    response = client.post(
        "/tickets/1/suggested-reply",
        json={
            "suggested_reply": "",
            "performed_by": "support-agent",
        },
    )

    assert response.status_code == 422

    manual_review_service.edit_suggested_reply.assert_not_called()
