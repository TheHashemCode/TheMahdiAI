# Intelligence Logic: RAG & Failover

## 1. 3-Level API Failover Workflow

The system uses **LiteLLM** and a **Circuit Breaker** to ensure high availability.

### Flow Logic
1. **Primary**: Attempt GPT-4o.
2. **Error Filter**: Catch 429 (Rate Limit), 500 (Server Error), or Timeouts.
3. **Backup 1**: If Primary fails, switch to Claude 3.5.
4. **Backup 2**: If Backup 1 fails, switch to Groq (Llama 3).
5. **Fallback**: If all fail, return "Service Busy" message.

### Circuit Breaker
- **Trigger**: 5 consecutive failures trips the breaker (`OPEN`).
- **Recovery**: Switches to `HALF_OPEN` after 5 minutes to test 1 request.

---

## 2. RAG Pipeline (Retrieval-Augmented Generation)

### Ingestion
- **Splitting**: `RecursiveCharacterTextSplitter` (chunk=1000, overlap=200).
- **Embedding**: `text-embedding-3-small` (1536 dims).
- **Storage**: Qdrant collection with cosine distance.

### Retrieval & Augmentation
- **Search**: Top 5 chunks with similarity > 0.75.
- **Context Injection**:
  ```
  [Reference Context]
  ...relevant chunks...
  
  [Conversation History]
  ...last 3 interactions...
  
  [User Question]
  ...current query...
  ```

---

## 3. Large Content Summarization
Use **Map-Reduce** pattern for transcripts exceeding 4000 tokens:
- **Map**: Summarize independent chunks.
- **Reduce**: Synthesize a coherent final summary.
