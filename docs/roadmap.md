# Project Roadmap & Milestones

## Phase 1: Foundation (Week 1–2)
- [x] Boilerplate setup (FastAPI + SQLModel).
- [x] Telegram Bot Core commands (`/start`, `/language`). (Supports 15+ global languages).
- [x] 3-Level AI Gateway with Failover & Streaming.
- [x] Admin Dashboard 1.0 (Users, Sessions, Full-page History).
- [x] Smart Quota & Rate Limiting (Redis + DB Fallback).
- [x] Concurrent Message Processing.
- [ ] Advanced Web Search integration.

## Phase 2: Intelligence & Media (Week 3–5)
- [ ] Qdrant Vector DB integration.
- [ ] RAG Pipeline (`/ask`) with PDF ingestion.
- [ ] YouTube Downloader (`/download`).
- [ ] Whisper Transcription & Basic Summarization.
- [ ] Vision API (`/captioning`).

## Phase 3: Automation & Scaling (Week 6–8)
- [ ] YouTube Notification Monitor (`/notif`).
- [ ] Map-Reduce Logic for long video summaries.
- [ ] Cost & Failover Analytics Dashboard.
- [ ] Prometheus + Grafana Monitoring.
- [ ] Production Deployment (Docker Compose).

---
### Acceptance Criteria
Each task must be verified with automated tests (unit/integration) before moving to the next phase.
