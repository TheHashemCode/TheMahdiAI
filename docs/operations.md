# Security & Operations

## 1. Security Controls

### Transport & API
- **TLS 1.3**: All traffic encrypted via Caddy/Nginx.
- **JWT (RS256)**: Admin dashboard authentication with short-lived tokens.
- **Webhook Secrets**: Cross-verification of Telegram source headers.

### Data
- **Rate Limiting**: Per-user sliding window via Redis.
- **Token Budget**: Daily hard limits stored in PostgreSQL.
- **Sanitization**: Pydantic validation for all LLM prompts to prevent injection.

---

## 2. Observability & Monitoring

### Metrics (Prometheus)
- `themahdiai_requests_total`: Total API hits.
- `themahdiai_tokens_consumed`: Running cost estimation.
- `themahdiai_failover_triggers`: High-frequency provider switching alerts.
- `themahdiai_circuit_breaker_state`: Real-time health gauge.

### Logging
- **Structured JSON Logs**: For automated ingestion.
- **Sentry Integration**: Exception tracking and stack trace snapshots.
