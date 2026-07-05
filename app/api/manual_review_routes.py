from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.manual_review_schema import (
    CategoryUpdateRequest,
    InternalNoteCreateRequest,
    PriorityUpdateRequest,
    StatusUpdateRequest,
    SuggestedReplyRegenerateRequest,
    SuggestedReplyUpdateRequest,
    TeamReassignmentRequest,
)
from app.services.manual_review_service import ManualReviewService


router = APIRouter(
    prefix="/tickets",
    tags=["manual-review"],
)

manual_review_service = ManualReviewService()


@router.post("/{ticket_id}/category")
def update_category(
    ticket_id: int,
    request: CategoryUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        ticket = manual_review_service.update_category(
            db,
            ticket_id=ticket_id,
            category=request.category,
            performed_by=request.performed_by,
        )

        return {
            "ticket_id": ticket.id,
            "category": ticket.category,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{ticket_id}/priority")
def update_priority(
    ticket_id: int,
    request: PriorityUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        ticket = manual_review_service.update_priority(
            db,
            ticket_id=ticket_id,
            priority=request.priority,
            performed_by=request.performed_by,
        )

        return {
            "ticket_id": ticket.id,
            "priority": ticket.priority,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{ticket_id}/team")
def reassign_team(
    ticket_id: int,
    request: TeamReassignmentRequest,
    db: Session = Depends(get_db),
):
    try:
        ticket = manual_review_service.reassign_team(
            db,
            ticket_id=ticket_id,
            assigned_team=request.assigned_team,
            performed_by=request.performed_by,
        )

        return {
            "ticket_id": ticket.id,
            "assigned_team": ticket.assigned_team,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{ticket_id}/status")
def update_status(
    ticket_id: int,
    request: StatusUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        ticket = manual_review_service.update_status(
            db,
            ticket_id=ticket_id,
            status=request.status,
            performed_by=request.performed_by,
        )

        return {
            "ticket_id": ticket.id,
            "status": ticket.status,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{ticket_id}/notes")
def add_internal_note(
    ticket_id: int,
    request: InternalNoteCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        internal_note = manual_review_service.add_internal_note(
            db,
            ticket_id=ticket_id,
            note=request.note,
            created_by=request.created_by,
        )

        return {
            "id": internal_note.id,
            "ticket_id": internal_note.ticket_id,
            "note": internal_note.note,
            "created_by": internal_note.created_by,
            "created_at": internal_note.created_at,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{ticket_id}/suggested-reply")
def edit_suggested_reply(
    ticket_id: int,
    request: SuggestedReplyUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        ticket = manual_review_service.edit_suggested_reply(
            db,
            ticket_id=ticket_id,
            suggested_reply=request.suggested_reply,
            performed_by=request.performed_by,
        )

        return {
            "ticket_id": ticket.id,
            "suggested_reply": ticket.suggested_reply,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{ticket_id}/suggested-reply/regenerate")
def regenerate_suggested_reply(
    ticket_id: int,
    request: SuggestedReplyRegenerateRequest,
    db: Session = Depends(get_db),
):
    try:
        ticket = manual_review_service.regenerate_suggested_reply(
            db,
            ticket_id=ticket_id,
            performed_by=request.performed_by,
        )

        return {
            "ticket_id": ticket.id,
            "suggested_reply": ticket.suggested_reply,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
