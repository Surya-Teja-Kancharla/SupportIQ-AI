import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import ParamSpec, TypeVar

from app.core.constants import LogEvent
from app.core.exceptions import RetryExhaustedError
from app.core.logging import get_logger, log_event


P = ParamSpec("P")
R = TypeVar("R")


logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    maximum_delay_seconds: float = 30.0
    exponential_base: float = 2.0
    jitter_seconds: float = 0.25

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        if self.initial_delay_seconds < 0:
            raise ValueError(
                "initial_delay_seconds cannot be negative."
            )

        if self.maximum_delay_seconds < 0:
            raise ValueError(
                "maximum_delay_seconds cannot be negative."
            )

        if self.exponential_base < 1:
            raise ValueError(
                "exponential_base must be at least 1."
            )

        if self.jitter_seconds < 0:
            raise ValueError(
                "jitter_seconds cannot be negative."
            )


class RetryExecutor:

    def __init__(
        self,
        policy: RetryPolicy,
        *,
        sleep_function: Callable[[float], None] = time.sleep,
        random_function: Callable[[float, float], float] = random.uniform,
    ) -> None:
        self.policy = policy
        self.sleep_function = sleep_function
        self.random_function = random_function

    def calculate_delay(self, failed_attempt: int) -> float:
        exponential_delay = (
            self.policy.initial_delay_seconds
            * (
                self.policy.exponential_base
                ** (failed_attempt - 1)
            )
        )

        bounded_delay = min(
            exponential_delay,
            self.policy.maximum_delay_seconds,
        )

        jitter = self.random_function(
            0,
            self.policy.jitter_seconds,
        )

        return bounded_delay + jitter

    def execute(
        self,
        operation: Callable[P, R],
        *args: P.args,
        retry_on: tuple[type[Exception], ...] = (Exception,),
        operation_name: str = "operation",
        **kwargs: P.kwargs,
    ) -> R:

        last_exception: Exception | None = None

        for attempt in range(
            1,
            self.policy.max_attempts + 1,
        ):
            try:
                return operation(*args, **kwargs)

            except retry_on as exc:
                last_exception = exc

                if attempt >= self.policy.max_attempts:
                    log_event(
                        logger,
                        logging.ERROR,
                        LogEvent.RETRIES_EXHAUSTED,
                        "Retry attempts exhausted.",
                        operation=operation_name,
                        attempts=attempt,
                        exception_type=type(exc).__name__,
                    )

                    raise RetryExhaustedError(
                        (
                            f"{operation_name} failed after "
                            f"{attempt} attempts."
                        ),
                        context={
                            "operation": operation_name,
                            "attempts": attempt,
                        },
                    ) from exc

                delay = self.calculate_delay(attempt)

                log_event(
                    logger,
                    logging.WARNING,
                    LogEvent.RETRY_SCHEDULED,
                    "Retry scheduled after operation failure.",
                    operation=operation_name,
                    attempt=attempt,
                    delay_seconds=delay,
                    exception_type=type(exc).__name__,
                )

                self.sleep_function(delay)

        raise RetryExhaustedError(
            f"{operation_name} failed.",
        ) from last_exception
