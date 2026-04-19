# API Specifications

## 1. Base URL & Versioning

```
Production:  https://api.themahdiai.com/api/v1
Development: http://localhost:8000/api/v1
```

## 2. Authentication

| Endpoint Group | Auth Method | Details |
|----------------|-------------|---------|
| Telegram Webhook | Webhook Secret Header | `X-Telegram-Bot-Api-Secret-Token` |
| Admin API | JWT Bearer Token | `Authorization: Bearer <token>` |
| Internal (Worker) | Service API Key | `X-Service-Key: <key>` |

## 3. Endpoint Specifications

### 3.1 Webhook

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/webhook/telegram` | Receive Telegram updates |

### 3.2 Admin — Users

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/admin/users` | List all users (paginated) |
| `GET` | `/admin/users/{id}` | Get user details + session info |
| `PATCH` | `/admin/users/{id}/limit` | Update daily token limit |
| `POST` | `/admin/users/{id}/ban` | Ban/unban user |

### 3.3 Admin — References (Knowledge Base)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/admin/references` | List all references |
| `POST` | `/admin/references` | Upload new reference (PDF/text) |
| `DELETE` | `/admin/references/{id}` | Remove reference + Qdrant vectors |
| `POST` | `/admin/references/{id}/reindex` | Re-process and re-index |

### 3.4 Admin — Analytics

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/admin/analytics/overview` | Dashboard overview stats |
| `GET` | `/admin/analytics/tokens` | Token usage over time |
| `GET` | `/admin/analytics/failover` | Failover event logs |
| `GET` | `/admin/analytics/costs` | Cost breakdown by provider |

### 3.5 Admin — Broadcast

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/admin/broadcasts` | List all broadcasts |
| `POST` | `/admin/broadcasts` | Create new broadcast |
| `POST` | `/admin/broadcasts/{id}/send` | Queue broadcast for sending |
| `GET` | `/admin/broadcasts/{id}/status` | Get delivery status |

### 3.6 Health & System

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check (DB, Redis, Qdrant) |
| `GET` | `/metrics` | Prometheus metrics |

## 4. Standard Response Format

```json
{
  "success": true,
  "data": { },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150
  },
  "error": null
}
```
