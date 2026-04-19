# Database Schema & Data Models

## 1. Entity Relationship Diagram

```mermaid
erDiagram
    users {
        uuid id PK
        bigint telegram_id UK
        varchar username
        varchar language
        int daily_token_limit
        int daily_token_used
        timestamptz created_at
    }

    chat_sessions {
        uuid id PK
        uuid user_id FK
        jsonb context_window
        boolean is_active
        timestamptz created_at
    }

    token_logs {
        uuid id PK
        uuid user_id FK
        varchar provider
        varchar model
        int total_tokens
        decimal cost_usd
        boolean is_failover
        timestamptz created_at
    }

    references {
        uuid id PK
        varchar title
        varchar source_type
        varchar status
        timestamptz created_at
    }

    broadcasts {
        uuid id PK
        text message_content
        varchar status
        int total_recipients
        timestamptz scheduled_at
    }

    youtube_monitors {
        uuid id PK
        uuid user_id FK
        varchar channel_id
        boolean is_active
        timestamptz last_checked_at
    }

    users ||--o{ chat_sessions : "has"
    users ||--o{ token_logs : "generates"
    users ||--o{ youtube_monitors : "subscribes"
    broadcasts ||--o{ broadcast_logs : "tracks"
```

## 2. Table Indexing

| Table | Index | Purpose |
|-------|-------|---------|
| `users` | `idx_users_telegram_id` | Fast lookup by Telegram ID |
| `chat_sessions` | `idx_sessions_user_active` | Retrieve current user session |
| `token_logs` | `idx_tokenlog_user_date` | Aggregate daily token usage |
| `references` | `idx_ref_status` | Filter by ingestion status |
