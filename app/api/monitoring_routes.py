from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.core.constants import WorkflowExecutionStatus
from app.schemas.monitoring_schema import (
    DatabaseHealthResponse,
    HealthResponse,
    WorkflowExecutionListResponse,
    WorkflowExecutionResponse,
    WorkflowMetricsResponse,
)
from app.services.monitoring_service import MonitoringService


router = APIRouter(
    tags=["monitoring"],
)


def get_monitoring_service(
    db: Session = Depends(get_db_session),
) -> MonitoringService:
    return MonitoringService(db)


@router.get(
    "/health",
    response_model=HealthResponse,
)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
    )


@router.get(
    "/health/database",
    response_model=DatabaseHealthResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Database unavailable.",
        },
    },
)
def get_database_health(
    service: MonitoringService = Depends(
        get_monitoring_service
    ),
) -> DatabaseHealthResponse:
    result = service.check_database_health()

    if result.status != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable.",
        )

    return result


@router.get(
    "/metrics",
    response_model=WorkflowMetricsResponse,
)
def get_metrics(
    service: MonitoringService = Depends(
        get_monitoring_service
    ),
) -> WorkflowMetricsResponse:
    return service.get_metrics()


@router.get(
    "/workflow-executions",
    response_model=WorkflowExecutionListResponse,
)
def list_workflow_executions(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    execution_status: WorkflowExecutionStatus | None = Query(
        default=None,
        alias="status",
    ),
    service: MonitoringService = Depends(
        get_monitoring_service
    ),
) -> WorkflowExecutionListResponse:
    return service.list_workflow_executions(
        page=page,
        page_size=page_size,
        status=(
            execution_status.value
            if execution_status is not None
            else None
        ),
    )


@router.get(
    "/workflow-executions/{execution_id}",
    response_model=WorkflowExecutionResponse,
)
def get_workflow_execution(
    execution_id: str,
    service: MonitoringService = Depends(
        get_monitoring_service
    ),
) -> WorkflowExecutionResponse:
    execution = service.get_workflow_execution(
        execution_id
    )

    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow execution not found.",
        )

    return execution
