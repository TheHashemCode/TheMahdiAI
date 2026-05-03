import time
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout_sec: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.failures = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = 0

    def record_failure(self):
        self.failures += 1
        logger.warning(f"CircuitBreaker recorded failure. Total failures: {self.failures}")
        if self.failures >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.last_failure_time = time.time()
            logger.error("CircuitBreaker tripped to OPEN state.")

    def record_success(self):
        if self.state != CircuitBreakerState.CLOSED:
            logger.info("CircuitBreaker recovered to CLOSED state.")
        self.failures = 0
        self.state = CircuitBreakerState.CLOSED

    def can_make_request(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
            
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout_sec:
                logger.info("CircuitBreaker entering HALF_OPEN state for testing.")
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
            
        if self.state == CircuitBreakerState.HALF_OPEN:
            return True  # Allow the test request
            
        return False

# Global instances for each provider
openai_circuit_breaker = CircuitBreaker()
anthropic_circuit_breaker = CircuitBreaker()
groq_circuit_breaker = CircuitBreaker()
