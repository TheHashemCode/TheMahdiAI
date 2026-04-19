# Feature Specifications

## 1. Telegram Bot Interface

### Commands
- `/start`: User onboarding.
- `/language [code]`: Change preference (`id`, `en`, `ar`).
- `/new_session`: Reset chat context.
- `/ask [query]`: Execute RAG search and AI response.
- `/download [url]`: YouTube video/audio downloader.
- `/notif [url]`: Subscribe to YouTube channel notifications.
- `/captioning`: Vision API for image description.
- `/search [query]`: Web search summarization.

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
- **Analytics**: Real-time KPI monitoring (DAU, Tokens, Costs).
- **User Management**: Limit adjustments and status control.
- **Reference Manager**: Knowledge base ingestion (PDF/Text).
- **Broadcast Tool**: Mass messaging with delivery tracking.
- **Failover Logs**: Real-time AI provider status.
