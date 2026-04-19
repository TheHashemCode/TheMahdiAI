# Feature Specifications

## 1. Telegram Bot Interface

### Commands
- `/start`: User onboarding and language selection.
- `/language [code]`: Change preference (English, Arabic, Persian, etc.).
- `/new_session`: Reset chat context and start fresh.
- `/ask [query]`: Execute RAG search and AI response (Phase 2).
- `/download [url]`: YouTube video/audio downloader (Phase 2).
- `/notif [url]`: Subscribe to YouTube channel notifications (Phase 3).
- `/captioning`: Vision API for image description (Phase 2).
- `/search [query]`: Basic web search summarization.

### Free-Text Logic
Messages without commands are treated as conversational inputs, maintaining session history and triggering RAG if relevant knowledge is identified.

---

## 2. YouTube Integration

### Flow: /download
1. **Queue**: Task sent to Redis worker.
2. **Download**: `yt-dlp` extracts content.
3. **Optimized Delivery**: 
   - Files < 50MB: Sent as Video.
   - Files > 50MB: Converted to Audio (MP3) before delivery.

### Flow: /notif (Auto-Summary)
1. **Monitor**: Periodic background check via worker.
2. **Transcribe**: Whisper API extracts text.
3. **Summarize**: Map-Reduce logic for long content.
4. **Notify**: Summary delivered to user.

---

## 3. Admin Dashboard (Next.js)

### Primary Modules
- **Analytics**: Real-time monitoring of DAU, Total Tokens, and Multi-provider Costs.
- **User Management**: Integrated user list with registration metadata and activity status.
- **Session History**: Dedicated full-page audit trail for all chat conversations.
- **System Orchestration**: Dynamic control over System Prompts, Token Limits, and Rate Limits.
- **Security Control**: Redis-backed quota enforcement with Database persistent fallback.
