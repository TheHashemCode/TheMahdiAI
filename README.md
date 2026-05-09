<p align="center">
  <img src="assets/logo.png" width="200" alt="TheMahdiAI Logo">
</p>

<h1 align="center">TheMahdiAI</h1>

<p align="center">
  <strong>Advanced The Ahmadi Religion of Peace and Light (AROPL) Knowledge Assistant powered by AI & RAG</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/LiteLLM-5A2D81?style=for-the-badge" alt="LiteLLM">
  <img src="https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
</p>

---

## 🌟 Overview

**TheMahdiAI** is an open-source, production-ready Telegram Bot designed to provide accurate, context-aware Islamic knowledge. It leverages a modern AI stack with RAG (Retrieval-Augmented Generation) and a robust 3-level failover gateway to ensure reliable and high-quality responses.

Built for the community, it integrates Quranic texts, authentic Hadiths, and scholarly references into a seamless, interactive chat experience.

## ✨ Key Features

- **🧠 Google NotebookLM Integration**: Direct API integration via `notebooklm-py` and Playwright for authenticating and querying Google's powerful RAG engine directly from Telegram.
- **🛡️ 3-Level AI Failover Gateway**: Automatic fallback between OpenAI, Anthropic, and Groq using LiteLLM and Circuit Breakers.
- **⚡ Parallel Processing & Streaming**: Concurrent message handling with progressive response delivery for a low-latency feel.
- **🔒 Smart Quota & Rate Limiting**: Built-in protection with Redis-based limits (minutely/daily) and persistent Database Fallback.
- **📊 Premium Admin Dashboard**: Modern Next.js dashboard to manage Notebooks, configure fallback chains, monitor real-time sessions, and audit detailed chat histories on dedicated pages.
- **🌐 Global Multi-lingual Support**: Native support for 15+ priority languages with manual custom entry.
- **🛠️ Dynamic Orchestration**: Hot-reload system prompts, Telegram bot menus, and fallback chains via the dashboard.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL & Redis
- [uv](https://github.com/astral-sh/uv) (Highly recommended for package management)
- Docker & Docker Compose (Optional, for easy infra setup)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/TheHashemCode/TheMahdiAI.git
   cd TheMahdiAI
   ```

2. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database credentials
   ```

3. **Install Dependencies**:
   ```bash
   pip install uv
   uv pip install -r requirements.txt
   ```

4. **Initialize Database**:
   ```bash
   alembic upgrade head
   ```

5. **Run API (Backend)**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. **Run Dashboard (Frontend)**:
   ```bash
   cd dashboard
   npm run dev
   ```
   *Dashboard will be available at [http://localhost:10313](http://localhost:10313)*

## ✅ Testing

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
make test
```

You can pass custom test args (without editing Makefile):

```bash
make test ARGS="-q -k quota"
```

### CI

Every push and pull request runs:

```bash
make test
```

The workflow uses Python 3.11 on GitHub Actions.

## 🤝 Contributing

- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution workflow.
- Use clear, small PRs with focused scope and tests.
- Keep secrets out of repository history (`.env*`, API keys, tokens).

### Development checklist

- Use `make test` before pushing.
- Update docs when behavior changes.
- Include or update unit tests for logic changes.

## 🏗️ Technical Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
- **AI Gateway**: [LiteLLM](https://docs.litellm.ai/)
- **Knowledge Engine**: Google NotebookLM (`notebooklm-py` + Playwright)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Vector DB**: [Qdrant](https://qdrant.tech/) (Planned)

## 📂 Project Structure

- `app/`: Core application logic (Bot handlers, AI Gateway, Models).
- `docs/`: Technical documentation and flowcharts.
- `contexts/`: Knowledge base for AI Agents and development best practices.
- `alembic/`: Database migration scripts.
- `assets/`: Project images and branding.
- `CONTRIBUTING.md`: Contributor guide.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---
<p align="center">
  <i>Developed by Wau Hashem & The Hashem Code Projects</i>
</p>
