# Intelligence Logic: RAG & Failover

## 1. 3-Level API Failover Workflow

The system uses **LiteLLM** and a **Circuit Breaker** to ensure high availability.

### Flow Logic
1. **Primary**: Attempt OpenAI (Supports custom `OPENAI_URL` via `api_base`).
2. **Error Filter**: Catch 429 (Rate Limit), 500 (Server Error), or Timeouts.
3. **Backup 1**: If Primary fails, switch to Anthropic.
4. **Backup 2**: If Backup 1 fails, switch to Groq.
5. **Fallback**: If all fail, return "Service Busy" message.

### Streaming Implementation
- **Mode**: Progressive editing (Simulated Streaming).
- **Interval**: Max 1 edit per second to avoid Telegram Rate Limits.
- **Visuals**: Uses a typing cursor (▍) during generation.

### Circuit Breaker
- **Trigger**: Recorded in `app/core/circuit_breaker.py`.
- **Logic**: Prevents cascading failures by short-circuiting providers that time out or return server errors.

---

## 2. RAG Pipeline (Retrieval-Augmented Generation)

### Ingestion
- **Splitting**: `RecursiveCharacterTextSplitter` (chunk=1000, overlap=200).
- **Embedding**: `text-embedding-3-small` (1536 dims).
- **Storage**: Qdrant collection with cosine distance.

### Retrieval & Augmentation
- **Search**: Top 5 chunks with similarity > 0.75.
- **System Prompt**: Dynamic injection via `bot_config` table. Supports placeholders `{user_name}` and `{user_language}`.
- **Context Injection**:
  ```
  [System Instruction]
  ...from DB (bot_config)...
  
  [Conversation History]
  ...last 20 messages (stored in chat_sessions.context_window)...
  
  [User Question]
  ...current query...
  ```

### Session Management
- **Persistence**: PostgreSQL (`chat_sessions` table).
- **Reset**: `/new_session` command marks the current session as inactive and starts a fresh one.
- **Logging**: Every interaction recorded in `token_logs` for cost/latency audit.

---

## 3. Large Content Summarization
Use **Map-Reduce** pattern for transcripts exceeding 4000 tokens:
- **Map**: Summarize independent chunks.
- **Reduce**: Synthesize a coherent final summary.
