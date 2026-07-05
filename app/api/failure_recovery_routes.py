from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.failure_recovery_schema import WorkflowRetryResponse
from app.services.failure_recovery_service import (
    FailureRecoveryService,
)


router = APIRouter(
    prefix="/workflow-executions",
    tags=["Failure Recovery"],
)


@router.post(
    "/{execution_id}/retry",
    response_model=WorkflowRetryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Workflow execution not found",
        },
        409: {
            "description": (
                "Workflow execution is not FAILED or has "
                "already been recovered"
            ),
        },
        500: {
            "description": "Retry execution failed",
        },
    },
)
def retry_workflow_execution(
    execution_id: str,
    db: Session = Depends(get_db),
) -> WorkflowRetryResponse:
    """
    Manually retry a failed workflow execution.
    """

    service = FailureRecoveryService(db)

    try:
        return service.retry_execution(execution_id)

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Retry execution failed.",
        ) from exc
