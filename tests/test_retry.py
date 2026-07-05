import pytest

from app.core.exceptions import RetryExhaustedError
from app.core.retry import RetryExecutor, RetryPolicy


def test_retry_policy_rejects_zero_attempts():
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)


def test_retry_executor_returns_success_immediately():
    attempts = []

    executor = RetryExecutor(
        RetryPolicy(max_attempts=3),
        sleep_function=lambda _: None,
        random_function=lambda _a, _b: 0,
    )

    def operation():
        attempts.append(1)
        return "success"

    result = executor.execute(operation)

    assert result == "success"
    assert len(attempts) == 1


def test_retry_executor_retries_until_success():
    attempts = []
    delays = []

    executor = RetryExecutor(
        RetryPolicy(
            max_attempts=3,
            initial_delay_seconds=1,
            exponential_base=2,
            jitter_seconds=0,
        ),
        sleep_function=delays.append,
        random_function=lambda _a, _b: 0,
    )

    def operation():
        attempts.append(1)

        if len(attempts) < 3:
            raise ConnectionError("temporary failure")

        return "success"

    result = executor.execute(
        operation,
        retry_on=(ConnectionError,),
    )

    assert result == "success"
    assert len(attempts) == 3
    assert delays == [1, 2]


def test_retry_executor_raises_after_exhaustion():
    executor = RetryExecutor(
        RetryPolicy(
            max_attempts=3,
            initial_delay_seconds=0,
            jitter_seconds=0,
        ),
        sleep_function=lambda _: None,
        random_function=lambda _a, _b: 0,
    )

    def operation():
        raise TimeoutError("timeout")

    with pytest.raises(RetryExhaustedError):
        executor.execute(
            operation,
            retry_on=(TimeoutError,),
            operation_name="test_operation",
        )


def test_retry_executor_does_not_retry_unlisted_exception():
    attempts = []

    executor = RetryExecutor(
        RetryPolicy(max_attempts=3),
        sleep_function=lambda _: None,
    )

    def operation():
        attempts.append(1)
        raise ValueError("invalid")

    with pytest.raises(ValueError):
        executor.execute(
            operation,
            retry_on=(ConnectionError,),
        )

    assert len(attempts) == 1


def test_calculate_delay_respects_maximum_delay():
    executor = RetryExecutor(
        RetryPolicy(
            initial_delay_seconds=10,
            maximum_delay_seconds=20,
            exponential_base=2,
            jitter_seconds=0,
        ),
        random_function=lambda _a, _b: 0,
    )

    assert executor.calculate_delay(1) == 10
    assert executor.calculate_delay(2) == 20
    assert executor.calculate_delay(3) == 20
