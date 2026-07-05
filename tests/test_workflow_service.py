from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy.orm import Session

from app.core.constants import (
    WorkflowExecutionStatus,
    WorkflowStage,
)
from app.core.exceptions import DuplicateWorkflowError
from app.schemas.email_schema import ParsedEmail
from app.schemas.normalized_ticket_schema import (
    NormalizationMetadata,
    NormalizedTicketAnalysis,
)
from app.schemas.reply_suggestion_schema import ReplySuggestionResponse
from app.schemas.ticket_decision_schema import (
    PriorityDecision,
    RoutingDecision,
)
from app.schemas.ticket_workflow_schema import TicketCreationResult
from app.services.workflow_service import WorkflowService


def build_email() -> ParsedEmail:
    return ParsedEmail(
        sender_name="Customer",
        sender_email="customer@example.com",
        subject="Production payment API unavailable",
        body=(
            "Our production payment API is completely unavailable "
            "and customers cannot complete payments."
        ),
        received_at=datetime.now(timezone.utc),
        message_id="<hour9-workflow-service@example.com>",
        attachments=[],
    )


def build_raw_analysis():
    return SimpleNamespace(
        customer_name="Customer",
        company="Example Corp",
        issue_summary="Production payment API unavailable",
        detailed_description=(
            "The production payment API is completely unavailable."
        ),
        category="Technical Support",
        priority="High",
        sentiment="Negative",
        product_service="Payment API",
        suggested_department="Technical Support",
        tags=["payment-api", "production-outage"],
        confidence_score=0.95,
    )


def build_normalized_analysis() -> NormalizedTicketAnalysis:
    return NormalizedTicketAnalysis(
        customer_name="Customer",
        company="Example Corp",
        issue_summary="Production payment API unavailable",
        detailed_description=(
            "The production payment API is completely unavailable."
        ),
        category="Technical Support",
        ai_recommended_priority="High",
        sentiment="Negative",
        product_service="Payment API",
        suggested_department="Technical Support",
        tags=["payment-api", "production-outage"],
        confidence_score=0.95,
        normalization_metadata=NormalizationMetadata(
            original_category="Technical Support",
            original_priority="High",
            original_sentiment="Negative",
            original_department="Technical Support",
            category_was_normalized=False,
            priority_was_normalized=False,
            sentiment_was_normalized=False,
            department_was_normalized=False,
            removed_duplicate_tags=0,
            removed_empty_tags=0,
            confidence_was_clamped=False,
        ),
    )


def build_priority_decision() -> PriorityDecision:
    return PriorityDecision(
        ai_recommended_priority="High",
        final_priority="Critical",
        applied_rule=(
            "Matched Critical priority business rule: production outage"
        ),
        was_overridden=True,
    )


def build_routing_decision() -> RoutingDecision:
    return RoutingDecision(
        category="Technical Support",
        assigned_team="Technical Support",
        applied_rule=(
            "Category 'Technical Support' routed to "
            "'Technical Support'"
        ),
    )


def build_reply_suggestion() -> ReplySuggestionResponse:
    return ReplySuggestionResponse(
        suggested_reply=(
            "Hello Customer, we are investigating the production "
            "payment API outage and will provide updates as soon as possible."
        )
    )


def build_ticket_creation_result() -> TicketCreationResult:
    return TicketCreationResult(
        ticket_id=101,
        ticket_number="SUP-20260705-TEST0001",
    )


def build_service():
    session = Mock(spec=Session)

    llm_service = Mock()
    ticket_analysis_normalizer = Mock()
    priority_service = Mock()
    routing_service = Mock()
    reply_suggestion_service = Mock()
    ticket_service = Mock()
    workflow_execution_repository = Mock()
    workflow_execution_service = Mock()

    raw_analysis = build_raw_analysis()
    normalized_analysis = build_normalized_analysis()
    priority_decision = build_priority_decision()
    routing_decision = build_routing_decision()
    reply_suggestion = build_reply_suggestion()
    ticket_creation_result = build_ticket_creation_result()

    workflow_execution_repository.get_by_message_id.return_value = None

    workflow_execution_service.get_by_message_id.side_effect = (
        lambda message_id: (
            workflow_execution_repository.get_by_message_id(
                message_id
            )
        )
    )

    workflow_execution = SimpleNamespace(
        id=1,
        execution_id="execution-123",
        message_id="<hour9-workflow-service@example.com>",
        ticket_id=None,
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        duration_ms=None,
        status=WorkflowExecutionStatus.RUNNING,
        current_stage=WorkflowStage.EMAIL_PARSED,
        retry_count=0,
        retry_exhausted=False,
        failure_stage=None,
        error_type=None,
        error_message=None,
        failed_at=None,
        parent_execution_id=None,
        attempt_number=1,
        execution_metadata=None,
    )

    def start_execution(*, message_id, stage):
        workflow_execution.message_id = message_id
        workflow_execution.current_stage = stage

        workflow_execution_repository.add(
            workflow_execution
        )

        return workflow_execution

    workflow_execution_service.start_execution.side_effect = (
        start_execution
    )

    workflow_execution_service.advance_stage.side_effect = (
        lambda execution, *, stage: (
            setattr(
                execution,
                "current_stage",
                stage,
            )
            or execution
        )
    )

    workflow_execution_service.attach_ticket.side_effect = (
        lambda execution, *, ticket_id: (
            setattr(
                execution,
                "ticket_id",
                ticket_id,
            ),
            setattr(
                execution,
                "current_stage",
                WorkflowStage.TICKET_CREATED,
            ),
            execution,
        )[-1]
    )

    workflow_execution_service.fail_execution.side_effect = (
        lambda execution, **kwargs: execution
    )

    workflow_execution_service.complete_execution.side_effect = (
        lambda execution: execution
    )

    llm_service.analyze_ticket.return_value = raw_analysis

    ticket_analysis_normalizer.normalize.return_value = (
        normalized_analysis
    )

    priority_service.assign_priority.return_value = (
        priority_decision
    )

    routing_service.route_ticket.return_value = (
        routing_decision
    )

    reply_suggestion_service.generate_suggestion.return_value = (
        reply_suggestion
    )

    ticket_service.create_ticket.return_value = (
        ticket_creation_result
    )

    service = WorkflowService(
        session=session,
        llm_service=llm_service,
        ticket_analysis_normalizer=(
            ticket_analysis_normalizer
        ),
        priority_service=priority_service,
        routing_service=routing_service,
        reply_suggestion_service=(
            reply_suggestion_service
        ),
        ticket_service=ticket_service,
        workflow_execution_service=(
            workflow_execution_service
        ),
        workflow_execution_repository=(
            workflow_execution_repository
        ),
    )

    return SimpleNamespace(
        service=service,
        session=session,
        llm_service=llm_service,
        normalizer=ticket_analysis_normalizer,
        priority_service=priority_service,
        routing_service=routing_service,
        reply_suggestion_service=reply_suggestion_service,
        ticket_service=ticket_service,
        workflow_repository=workflow_execution_repository,
        workflow_execution_service=workflow_execution_service,
        workflow_execution=workflow_execution,
        raw_analysis=raw_analysis,
        normalized_analysis=normalized_analysis,
        priority_decision=priority_decision,
        routing_decision=routing_decision,
        reply_suggestion=reply_suggestion,
        ticket_creation_result=ticket_creation_result,
    )


def test_process_email_checks_message_id_before_ai_analysis():
    context = build_service()
    email = build_email()

    events = []

    context.workflow_repository.get_by_message_id.side_effect = (
        lambda message_id: events.append(
            "idempotency_check"
        )
    )

    context.llm_service.analyze_ticket.side_effect = (
        lambda request: (
            events.append("ai_analysis"),
            context.raw_analysis,
        )[1]
    )

    context.service.process_email(email)

    assert events[:2] == [
        "idempotency_check",
        "ai_analysis",
    ]


def test_process_email_rejects_duplicate_message_id():
    context = build_service()
    email = build_email()

    context.workflow_repository.get_by_message_id.return_value = (
        SimpleNamespace(id=1)
    )

    with pytest.raises(DuplicateWorkflowError):
        context.service.process_email(email)


def test_duplicate_message_id_does_not_call_llm():
    context = build_service()

    context.workflow_repository.get_by_message_id.return_value = (
        SimpleNamespace(id=1)
    )

    with pytest.raises(DuplicateWorkflowError):
        context.service.process_email(build_email())

    context.llm_service.analyze_ticket.assert_not_called()


def test_duplicate_message_id_does_not_create_ticket():
    context = build_service()

    context.workflow_repository.get_by_message_id.return_value = (
        SimpleNamespace(id=1)
    )

    with pytest.raises(DuplicateWorkflowError):
        context.service.process_email(build_email())

    context.ticket_service.create_ticket.assert_not_called()


def test_process_email_calls_ticket_analysis():
    context = build_service()
    email = build_email()

    context.service.process_email(email)

    context.llm_service.analyze_ticket.assert_called_once()


def test_process_email_normalizes_analysis():
    context = build_service()

    context.service.process_email(build_email())

    context.normalizer.normalize.assert_called_once_with(
        context.raw_analysis
    )


def test_process_email_assigns_priority():
    context = build_service()

    context.service.process_email(build_email())

    context.priority_service.assign_priority.assert_called_once_with(
        context.normalized_analysis
    )


def test_process_email_routes_ticket():
    context = build_service()

    context.service.process_email(build_email())

    context.routing_service.route_ticket.assert_called_once_with(
        context.normalized_analysis
    )


def test_process_email_generates_reply_suggestion():
    context = build_service()
    email = build_email()

    context.service.process_email(email)

    (
        context.reply_suggestion_service
        .generate_suggestion
        .assert_called_once_with(
            email=email,
            analysis=context.normalized_analysis,
        )
    )


def test_process_email_creates_ticket():
    context = build_service()
    email = build_email()

    context.service.process_email(email)

    context.ticket_service.create_ticket.assert_called_once_with(
        email=email,
        analysis=context.normalized_analysis,
        priority_decision=context.priority_decision,
        routing_decision=context.routing_decision,
        reply_suggestion=context.reply_suggestion,
    )


def test_process_email_creates_workflow_execution():
    context = build_service()

    result = context.service.process_email(build_email())

    context.workflow_repository.add.assert_called_once()

    execution = (
        context.workflow_repository.add.call_args.args[0]
    )

    assert execution.message_id == (
        "<hour9-workflow-service@example.com>"
    )
    assert execution.ticket_id == 101
    assert execution.status.value == "RUNNING"
    assert (
        execution.current_stage
        == WorkflowStage.TICKET_CREATED
    )
    assert result.execution_id == execution.execution_id


def test_process_email_commits_once_after_complete_success():
    context = build_service()

    context.service.process_email(build_email())

    context.session.commit.assert_called_once_with()
    context.session.rollback.assert_not_called()


def test_process_email_returns_processing_result():
    context = build_service()

    result = context.service.process_email(build_email())

    assert result.ticket_id == 101
    assert (
        result.ticket_number
        == "SUP-20260705-TEST0001"
    )
    assert result.message_id == (
        "<hour9-workflow-service@example.com>"
    )
    assert result.analysis == context.normalized_analysis
    assert (
        result.priority_decision
        == context.priority_decision
    )
    assert (
        result.routing_decision
        == context.routing_decision
    )
    assert (
        result.reply_suggestion
        == context.reply_suggestion
    )


def test_process_email_reuses_passed_workflow_execution():
    context = build_service()
    email = build_email()

    workflow_execution = SimpleNamespace(
        id=1,
        execution_id="execution-123",
        message_id=email.message_id,
        ticket_id=None,
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        duration_ms=None,
        status=WorkflowExecutionStatus.RUNNING,
        current_stage=WorkflowStage.EMAIL_PARSED,
        retry_count=0,
        retry_exhausted=False,
        failure_stage=None,
        error_type=None,
        error_message=None,
        failed_at=None,
        parent_execution_id=None,
        attempt_number=1,
        execution_metadata=None,
    )

    result = context.service.process_email(
        email,
        workflow_execution=workflow_execution,
    )

    (
        context.workflow_execution_service
        .start_execution
        .assert_not_called()
    )

    (
        context.workflow_execution_service
        .advance_stage
        .assert_any_call(
            workflow_execution,
            stage=WorkflowStage.AI_ANALYSIS_STARTED,
        )
    )

    (
        context.workflow_execution_service
        .attach_ticket
        .assert_called_once()
    )

    assert result.execution_id == "execution-123"


def test_process_email_rejects_mismatched_execution_message_id():
    context = build_service()
    email = build_email()

    workflow_execution = MagicMock()
    workflow_execution.message_id = "<different@example.com>"

    with pytest.raises(
        ValueError,
        match="message_id does not match",
    ):
        context.service.process_email(
            email,
            workflow_execution=workflow_execution,
        )

    (
        context.workflow_execution_service
        .start_execution
        .assert_not_called()
    )


@pytest.mark.parametrize(
    ("dependency_name", "method_name"),
    [
        ("llm_service", "analyze_ticket"),
        ("normalizer", "normalize"),
        ("priority_service", "assign_priority"),
        ("routing_service", "route_ticket"),
        (
            "reply_suggestion_service",
            "generate_suggestion",
        ),
        ("ticket_service", "create_ticket"),
    ],
)
def test_downstream_failure_rolls_back(
    dependency_name,
    method_name,
):
    context = build_service()

    dependency = getattr(
        context,
        dependency_name,
    )

    original_error = RuntimeError(
        f"{dependency_name} failure"
    )

    getattr(
        dependency,
        method_name,
    ).side_effect = original_error

    with pytest.raises(RuntimeError) as exc_info:
        context.service.process_email(build_email())

    assert exc_info.value is original_error

    context.session.rollback.assert_called_once_with()
    context.session.commit.assert_not_called()


def test_failed_workflow_does_not_commit():
    context = build_service()

    context.ticket_service.create_ticket.side_effect = (
        RuntimeError(
            "ticket creation failed"
        )
    )

    with pytest.raises(RuntimeError):
        context.service.process_email(build_email())

    context.session.commit.assert_not_called()


def test_workflow_preserves_original_typed_exception():
    context = build_service()

    class TypedApplicationError(Exception):
        pass

    original_error = TypedApplicationError(
        "typed application failure"
    )

    context.priority_service.assign_priority.side_effect = (
        original_error
    )

    with pytest.raises(
        TypedApplicationError
    ) as exc_info:
        context.service.process_email(build_email())

    assert exc_info.value is original_error


def test_process_email_executes_complete_pipeline_in_order():
    context = build_service()

    manager = Mock()

    manager.attach_mock(
        context.workflow_repository.get_by_message_id,
        "idempotency_check",
    )
    manager.attach_mock(
        context.workflow_repository.add,
        "persist_execution",
    )
    manager.attach_mock(
        context.llm_service.analyze_ticket,
        "analyze_ticket",
    )
    manager.attach_mock(
        context.normalizer.normalize,
        "normalize",
    )
    manager.attach_mock(
        context.priority_service.assign_priority,
        "assign_priority",
    )
    manager.attach_mock(
        context.routing_service.route_ticket,
        "route_ticket",
    )
    manager.attach_mock(
        (
            context.reply_suggestion_service
            .generate_suggestion
        ),
        "generate_suggestion",
    )
    manager.attach_mock(
        context.ticket_service.create_ticket,
        "create_ticket",
    )
    manager.attach_mock(
        context.session.commit,
        "commit",
    )

    context.service.process_email(build_email())

    method_names = [
        item[0]
        for item in manager.mock_calls
    ]

    assert method_names == [
        "idempotency_check",
        "persist_execution",
        "analyze_ticket",
        "normalize",
        "assign_priority",
        "route_ticket",
        "generate_suggestion",
        "create_ticket",
        "commit",
    ]


def test_process_email_does_not_complete_workflow_execution():
    context = build_service()

    context.service.process_email(build_email())

    (
        context.workflow_execution_service
        .complete_execution
        .assert_not_called()
    )


def test_execution_start_failure_propagates_without_business_rollback():
    context = build_service()

    original_error = RuntimeError(
        "workflow execution persistence failure"
    )

    context.workflow_repository.add.side_effect = (
        original_error
    )

    with pytest.raises(RuntimeError) as exc_info:
        context.service.process_email(build_email())

    assert exc_info.value is original_error

    context.session.rollback.assert_not_called()
    context.session.commit.assert_not_called()

    context.llm_service.analyze_ticket.assert_not_called()
    context.ticket_service.create_ticket.assert_not_called()
