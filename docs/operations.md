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

---

## 3. NotebookLM Operations

### Playwright Authentication
Google NotebookLM requires browser-based cookies (`notebooklm-py` + Playwright) because it doesn't have an official REST API.

1. **Initial Login**: 
   - By default, Playwright runs in headless mode (`PLAYWRIGHT_HEADLESS=true`).
   - If running locally, you can click "Login via UI (Server)" in the admin dashboard. Set `PLAYWRIGHT_HEADLESS=false` in `.env` to see the browser pop up and login to your Google account.
   - If running on a headless VPS (e.g., Ubuntu server), the UI login will fail if headless is false. You should log in locally, then upload the `scratch/notebooklm_storage.json` cookie file securely to the production server.

### Anti-Ban Strategy
- **Smart Queuing**: Google restricts concurrent queries to the same Notebook. The application uses a `defaultdict(asyncio.Lock)` in `NotebookService` to process queries sequentially per Notebook. This allows high throughput across *different* notebooks while preventing HTTP 429 bans on individual notebooks.
