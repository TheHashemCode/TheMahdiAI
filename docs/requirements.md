# Product Requirements & Goals

## 1. Executive Summary

**TheMahdiAI** adalah sebuah Telegram Bot yang menggunakan Retrieval-Augmented Generation (RAG) untuk menyediakan asisten AI berbasis referensi keislaman. Bot ini mendukung:

- **Conversational AI** dengan konteks dari knowledge base yang dikurasi.
- **YouTube Integration** — download, transkripsi (Whisper), dan auto-summarization konten.
- **3-Level API Failover** — jaminan high-availability melalui cascading AI provider (GPT-4o → Claude 3.5 → Groq/Llama3).
- **Admin Dashboard** — manajemen referensi, user analytics, dan broadcast tool.

### Target User
| Persona | Deskripsi |
|---------|-----------|
| **End User** | Pengguna Telegram yang ingin bertanya seputar topik keislaman dengan jawaban berbasis referensi. |
| **Admin** | Pengelola konten yang meng-upload referensi, memantau usage, dan mengelola broadcast. |

---

## 2. Goals & Success Metrics

### 2.1 Product Goals

| # | Goal | Measurement |
|---|------|-------------|
| G1 | Menyediakan jawaban AI akurat berbasis referensi | RAG relevance score ≥ 0.85 |
| G2 | High availability AI response | Uptime ≥ 99.5% (measured per month) |
| G3 | Latensi respons yang cepat | p95 response time ≤ 5 detik |
| G4 | Scalable user management | Support ≥ 10,000 registered users |
| G5 | Cost-efficient token usage | Average cost per query ≤ $0.005 |

### 2.2 Key Performance Indicators (KPI)

| KPI | Target | Frequency |
|-----|--------|-----------|
| Daily Active Users (DAU) | ≥ 200 (Phase 1) | Daily |
| Average queries per user | ≥ 3/day | Weekly |
| Failover trigger rate | ≤ 5% of total requests | Weekly |
| Knowledge base coverage | ≥ 500 documents ingested | Monthly |
| Bot response satisfaction | ≥ 4.2/5 (via feedback command) | Monthly |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Bot response latency (p50) | 2s or less | From message received to response sent |
| Bot response latency (p95) | 5s or less | Including RAG retrieval |
| RAG retrieval latency | 500ms or less | Qdrant vector search |
| API throughput | 100 req/s or more | Under normal load |
| YouTube download start | 10s or less | Queue to download start |

### 3.2 Availability

| Metric | Target |
|--------|--------|
| System uptime | 99.5% monthly or better |
| Planned maintenance window | 30 min/month or less |
| RTO (Recovery Time Objective) | 15 minutes or less |
| RPO (Recovery Point Objective) | 1 hour or less |

### 3.3 Scalability

| Dimension | Phase 1 | Phase 3+ |
|-----------|---------|----------|
| Concurrent users | 100 | 1,000 |
| Registered users | 1,000 | 10,000 |
| Knowledge base documents | 100 | 1,000+ |
| Daily API calls | 5,000 | 50,000+ |

### 3.4 Rate Limiting Strategy

| Scope | Limit | Window | Storage |
|-------|-------|--------|---------|
| Per-user messages | 20 | 1 minute | Redis (sliding window) |
| Per-user daily tokens | Configurable (default: 100,000) | 24 hours | PostgreSQL |
| Admin API | 100 | 1 minute | Redis |
| Broadcast sending | 30 messages/second | — | Redis queue |
