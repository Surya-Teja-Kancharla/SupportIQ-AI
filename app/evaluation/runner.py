import json
from datetime import datetime, timezone
from pathlib import Path

from app.schemas.email_schema import ParsedEmail
from app.schemas.evaluation_schema import (
    EvaluationCase,
    EvaluationCaseResult,
    EvaluationDataset,
    EvaluationReport,
)
from app.schemas.ticket_analysis_schema import TicketAnalysisRequest
from app.services.llm_service import LLMService

from app.evaluation.metrics import calculate_evaluation_metrics


class EvaluationRunner:

    def __init__(
        self,
        llm_service: LLMService,
        prompt_version: str,
    ) -> None:
        self.llm_service = llm_service
        self.prompt_version = prompt_version

    def load_dataset(
        self,
        dataset_path: Path,
    ) -> EvaluationDataset:

        with dataset_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        return EvaluationDataset.model_validate(payload)

    def evaluate_case(
        self,
        case: EvaluationCase,
    ) -> EvaluationCaseResult:

        email = ParsedEmail(
            message_id=f"<evaluation-{case.case_id}@supportiq.local>",
            sender_name=case.sender_name,
            sender_email=case.sender_email,
            subject=case.subject,
            body=case.body,
            received_at=datetime.now(timezone.utc),
        )

        request = TicketAnalysisRequest(
            email=email,
            attachment_text=case.attachment_text,
        )

        try:
            analysis = self.llm_service.analyze_ticket(request)

        except Exception as exc:
            return EvaluationCaseResult(
                case_id=case.case_id,
                case_type=case.case_type,
                success=False,
                expected=case.expected,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

        category_correct = (
            analysis.category == case.expected.category
        )

        priority_correct = (
            analysis.priority == case.expected.priority
        )

        sentiment_correct = (
            analysis.sentiment == case.expected.sentiment
        )

        department_correct = (
            analysis.suggested_department
            == case.expected.suggested_department
        )

        return EvaluationCaseResult(
            case_id=case.case_id,
            case_type=case.case_type,
            success=True,
            expected=case.expected,
            actual_category=analysis.category,
            actual_priority=analysis.priority,
            actual_sentiment=analysis.sentiment,
            actual_department=analysis.suggested_department,
            category_correct=category_correct,
            priority_correct=priority_correct,
            sentiment_correct=sentiment_correct,
            department_correct=department_correct,
            all_labels_correct=all(
                (
                    category_correct,
                    priority_correct,
                    sentiment_correct,
                    department_correct,
                )
            ),
            confidence_score=analysis.confidence_score,
        )

    def run(
        self,
        dataset_path: Path,
    ) -> EvaluationReport:

        dataset = self.load_dataset(dataset_path)

        results = [
            self.evaluate_case(case)
            for case in dataset.cases
        ]

        metrics, case_type_metrics = (
            calculate_evaluation_metrics(results)
        )

        return EvaluationReport(
            dataset_name=dataset.dataset_name,
            dataset_version=dataset.dataset_version,
            prompt_version=self.prompt_version,
            metrics=metrics,
            case_type_metrics=case_type_metrics,
            results=results,
        )
