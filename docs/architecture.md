# System Architecture & Infrastructure

## 1. Layer Overview

```mermaid
graph TD
    subgraph "User Layer"
        TG["Telegram Bot API\n(python-telegram-bot v20+)"]
    end

    subgraph "Application Layer"
        BE["Backend Core\n(FastAPI + Uvicorn)"]
        WK["Background Worker\n(ARQ / Celery)"]
    end

    subgraph "Intelligence Layer"
        RAG["RAG Engine\n(LangChain)"]
        AI_GW["AI Gateway\n(LiteLLM)"]
        NBLM["NotebookLM Client\n(notebooklm-py)"]
        WHISPER["Transcription\n(Whisper API / faster-whisper)"]
    end

    subgraph "Data Layer"
        DB[("PostgreSQL 16\n(Users, Logs, Settings)")]
        VS[("Qdrant\n(Vector Store)")]
        CACHE[("Redis 7\n(Session, Queue, Rate Limit)")]
        S3["Object Storage\n(MinIO / Local FS)\n(PDFs, Audio, Video)"]
        PW["Playwright Auth\n(Local Storage JSON)"]
    end

    subgraph "AI Providers - Failover Chain"
        P["Primary: GPT-4o"]
        B1["Backup 1: Claude 3.5 Sonnet"]
        B2["Backup 2: Groq - Llama 3"]
        GN["Google NotebookLM"]
    end

    subgraph "External APIs"
        YT["YouTube\n(yt-dlp)"]
    end

    TG <--> BE
    BE --> RAG
    BE --> NBLM
    BE --> WK
    RAG --> VS
    RAG --> AI_GW
    NBLM --> PW
    NBLM --> GN
    AI_GW --> P
    AI_GW --> B1
    AI_GW --> B2
    BE --> DB
    BE --> CACHE
    WK --> YT
    WK --> WHISPER
    WK --> S3
    WK --> CACHE
```

---

## 2. Project Directory Structure

```
themahdiai/
├── app/
│   ├── main.py                    # FastAPI application factory
│   ├── api/                       # API Endpoints
│   ├── bot/                       # Telegram Bot Handlers
│   ├── core/                      # Global logic (AI Gateway, Rate Limit)
│   ├── services/                  # Business Logic (RAG, YT, Summarizer)
│   ├── models/                    # SQLModel database schemas
│   └── utils/                     # Helpers
├── dashboard/                     # Admin Dashboard (Next.js)
├── docker/                        # Dockerfiles
├── docs/                          # Human-facing documentation
├── contexts/                      # AI-facing context/best practices
└── docker-compose.prod.yml
```

---

## 3. Deployment Topology

```mermaid
graph TD
    subgraph "Internet"
        USER["Telegram Users"]
        ADMIN["Admin Browser"]
    end

    subgraph "Reverse Proxy"
        CF["Cloudflare Tunnel\nwebsite.com"]
    end

    subgraph "Docker Host - PVE LXC"
        subgraph "docker-compose"
            API["API Container\nport 8000"]
            WK["Worker Container"]
            DASH["Dashboard\nport 3000"]
            PG["PostgreSQL\nport 5432"]
            RD["Redis\nport 6379"]
            QD["Qdrant\nport 6333"]
        end
    end

    USER -->|"HTTPS"| CF
    ADMIN -->|"HTTPS"| CF
    CF -->|"port 8000"| API
    CF -->|"port 3000"| DASH
    API --> PG
    API --> RD
    API --> QD
    WK --> PG
    WK --> RD
    WK --> QD
```

---

## 4. Resource Requirements

| Service | CPU | RAM | Storage |
|---------|-----|-----|---------|
| API | 2 vCPU | 1 GB | 500 MB |
| Worker | 2 vCPU | 2 GB | 5 GB (temp) |
| Dashboard | 1 vCPU | 512 MB | 200 MB |
| PostgreSQL | 2 vCPU | 2 GB | 10 GB+ |
| Redis | 1 vCPU | 256 MB | 100 MB |
| Qdrant | 2 vCPU | 2 GB | 5 GB+ |
| **Total** | **10 vCPU** | **8 GB** | **~21 GB** |
