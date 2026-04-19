# TheMahdiAI

AI-Powered Telegram Bot based on RAG (Retrieval-Augmented Generation) with YouTube Integration and 3-Level API Failover.

## Project Structure

- `app/`: Backend Core (FastAPI).
- `docs/`: Technical documentation for humans.
- `contexts/`: Documentation for AI Agents (Best practices, logic workflows, environment).
- `dashboard/`: Admin Dashboard (Next.js).
- `docker/`: Dockerfiles and container configurations.

## Getting Started

1. **Clone the repository.**
2. **Setup Environment**: Copy `contexts/environment.md` contents to a `.env` file.
3. **Run Services**:
   ```bash
   docker compose up -d postgres redis qdrant
   ```
4. **Run API**:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## Documentation Index

- [Product Roadmap](docs/roadmap.md)
- [System Architecture](docs/architecture.md)
- [API Specifications](docs/api_spec.md)
- [Database Schema](docs/database.md)
- [Intelligence Logic (RAG & Failover)](contexts/ai_logic.md)

---
*Built with love for Islamic Knowledge.*
