# Environment Configuration Guide

This file contains the template for the `.env` file required to run the application.

## 1. Application Core
```env
APP_NAME=TheMahdiAI
APP_ENV=production
APP_SECRET_KEY=<random-64-char-hex>
APP_HOST=0.0.0.0
APP_PORT=8000
```

## 2. AI Providers (Failover Chain)
```env
# Primary
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_URL=http://... # Optional: custom API base for OpenAI-compatible proxies

# Backup 1
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Backup 2
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
```

## 3. Databases
```env
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://...

# Redis
REDIS_URL=redis://...

# Qdrant (Vector DB)
QDRANT_HOST=qdrant
QDRANT_API_KEY=...
```

## 4. Bot & External
```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_WEBHOOK_URL=https://...
# Note: Ensure DB uses BigInteger for telegram_id to support 10-digit IDs.
S3_BUCKET_NAME=themahdi-ai
```
