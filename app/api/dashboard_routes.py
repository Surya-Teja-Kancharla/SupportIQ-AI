from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_dashboard_service
from app.schemas.dashboard_schema import TicketFilters
from app.services.dashboard_service import DashboardService


router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)

BASE_DIR = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(
    directory=str(BASE_DIR / "app" / "templates")
)


@router.get(
    "/tickets",
    response_class=HTMLResponse,
)
def ticket_list(
    request: Request,
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    category: str | None = Query(default=None),
    assigned_team: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    dashboard_service: DashboardService = Depends(
        get_dashboard_service
    ),
):
    filters = TicketFilters(
        status=status or None,
        priority=priority or None,
        category=category or None,
        assigned_team=assigned_team or None,
        limit=limit,
        offset=offset,
    )

    result = dashboard_service.list_tickets(filters)

    return templates.TemplateResponse(
        request=request,
        name="ticket_list.html",
        context={
            "result": result,
            "filters": filters,
        },
    )


@router.get(
    "/tickets/{ticket_id}",
    response_class=HTMLResponse,
)
def ticket_detail(
    request: Request,
    ticket_id: int,
    dashboard_service: DashboardService = Depends(
        get_dashboard_service
    ),
):
    ticket = dashboard_service.get_ticket_detail(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    return templates.TemplateResponse(
        request=request,
        name="ticket_detail.html",
        context={
            "ticket": ticket,
        },
    )
