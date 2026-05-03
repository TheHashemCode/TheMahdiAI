# Changelog

## [Phase 2.0] - 2026-04-26
### Added
- **Google NotebookLM Integration**: Added `notebooklm-py` with Playwright browser-based authentication to query NotebookLM directly.
- **Smart Fallback Chain**: Introduced a configurable fallback system (up to 5 notebooks) for `/ask` command to ensure at least 2 references are retrieved for every query.
- **Anti-Banned Queue**: Added `asyncio.Lock()` in `NotebookService` to process queries sequentially and avoid rate-limiting/banning from Google.
- **Notebooks Dashboard**: New `/notebooks` page in the Next.js dashboard to manage connections, sync notebooks, add reference sources (URLs), and test queries.
- **Interactive History Modal**: Clickable table rows in the dashboard history that reveal full Markdown answers and detailed reference tracking.
- **Automated Citations**: AI responses automatically append "📚 Referensi Sumber" with bolded inline citations mapped to source titles.

### Fixed
- **Playwright Headless Mode**: Added `PLAYWRIGHT_HEADLESS` environment variable (defaults to true) to safely run in non-GUI server environments.
- **Message Truncation**: Fixed Telegram 4000 character limits to truncate nicely on newlines and spaces, preserving markdown blocks.
- **Query Safety Checks**: Added checks for empty `result` and `answer` returns from Google to prevent silent crashes.
- **Config Security**: Hardened `/admin/configs` POST endpoint by adding an `ALLOWED_CONFIG_KEYS` validation list to prevent arbitrary database updates.
- **Redis Quota Race Condition**: Used `nx=True` to prevent duplicate writes during token hydration when server scales horizontally.

### Changed
- **Async DB Migration**: Updated Telegram Bot backend methods and background services to properly use `async_session_maker` instead of standard sync `Session`.
- **Per-Notebook Lock**: Refactored the NotebookService lock to a per-notebook basis `defaultdict(asyncio.Lock)` enabling fast concurrent queries for different notebooks while preventing bans on a single notebook.
- **Deprecated Datetime**: Swept all `datetime.utcnow()` usage across the app and replaced it with timezone-aware `datetime.now(timezone.utc)`.
- **Environment Variables**: Replaced hardcoded `localhost:8000` strings in Next.js with `process.env.NEXT_PUBLIC_API_URL` for flexible production deployments.

## [Phase 1.1] - 2026-04-19
### Added
- **Admin Dashboard**: Full-featured Next.js 15+ dashboard with glassmorphism design.
- **Session Management**: Dedicated full-page view for chat histories with interactive breadcrumbs.
- **Security & Quotas**: 
    - Redis-based Rate Limiting (20 req/min default).
    - Daily Request Quotas (500 req/day default).
    - Daily Token Quotas (1M tokens/day default).
    - Database Fallback for all security limits (works even if Redis is down).
- **Two-Layer Sync**: Real-time synchronization between Redis (fast-layer) and PostgreSQL (persistent-layer) for usage tracking.
- **Concurrent Processing**: Bot now handles multiple messages simultaneously via `concurrent_updates=True`.
- **System Orchestration**: Added a dynamic settings editor in the dashboard to manage system prompts, token limits, and rate limits without code changes.
- **Global reach**: Default language set to English with support for 15+ priority languages.

### Fixed
- Telegram Markdown rendering for bold/italic/lists (`parse_mode` integration).
- Streaming usage tracking: `stream_options` integration for accurate token counting.
- Hydration mismatch in Dashboard UI.
- Layout shifting in chat history view.

### Changed
- Migrated Dashboard from `styled-jsx` to **CSS Modules** for better maintainability and performance.
- Replaced Chat History Modal with a Dedicated Dynamic Route page for a "relaxed" reading experience.
- Updated all bot notifications and error messages to English.
