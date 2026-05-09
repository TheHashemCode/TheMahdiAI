import time

from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerState


def test_circuit_breaker_reaches_open_state_after_threshold():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=60)

    assert cb.can_make_request() is True

    cb.record_failure()
    cb.record_failure()

    assert cb.state == CircuitBreakerState.OPEN
    assert cb.failures == 2

    # Still blocked while open and still within timeout
    assert cb.can_make_request() is False


def test_circuit_breaker_recovers_from_open_to_closed(monkeypatch):
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout_sec=0)

    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN

    # With zero recovery timeout, it should immediately allow a test request
    assert cb.can_make_request() is True
    assert cb.state == CircuitBreakerState.HALF_OPEN

    cb.record_success()
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.failures == 0
