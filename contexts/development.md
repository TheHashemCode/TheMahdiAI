# Development Context & Best Practices

## 1. Technical Decisions & Rationale

- **LiteLLM**: Unified API for all providers, simplifies failover logic.
- **NotebookLM**: Integrated via `notebooklm-py` and Playwright for private RAG. Authentication depends on a local JSON cookie file to bypass Google's lack of an official REST API.
- **Qdrant**: High performance, native filter support, efficient vector management.
- **SQLModel**: Pydantic-friendly ORM, minimizes code duplication between schemas and models.
- **ARQ**: Lightweight Redis-based async queue, better performance than Celery for simple tasks.
- **Async Locks**: Uses `defaultdict(asyncio.Lock)` for API operations that do not support true concurrency (like scraping Google NotebookLM) to avoid HTTP 429 errors.

## 2. Best Practices for Developers/Agents

### Code Quality
- **Branching**: Use `feat/...` or `fix/...`. Never commit directly to `main`.
- **Typing**: Mandatory type hints for all function signatures.
- **Pydantic**: Use for every external input/output and environment config.
- **Dependency Management**: Use `uv` (`uv pip install`) for faster development rounds.
- **Migrations**: Always use `alembic revision --autogenerate` for schema changes.

### AI Interaction
- When querying RAG (`/ask`), always ensure the `score_threshold` is respected to avoid hallucinated context.
- Keep the `context_window` stable (currently last 20 messages) in `chat_sessions` to balance memory and token cost.

### Error Handling & Concurrency
- Never return raw AI errors to the user. Wrap in human-readable messages (Indonesian primary).
- Log every failover event for periodic cost/performance review.
- Always use atomic operations (`nx=True`) in Redis when hydrating data from PostgreSQL to avoid race conditions when the backend scales horizontally.

---

## 3. Risks & Mitigations

- **Cost Spike**: Enforce daily token limits per user via PostgreSQL.
- **Hallucination**: High similarity threshold (0.75) for RAG chunks.
- **YouTube Block**: Maintain updated `yt-dlp` and use cookie authentication if necessary.
