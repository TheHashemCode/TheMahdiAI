# Changelog

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
