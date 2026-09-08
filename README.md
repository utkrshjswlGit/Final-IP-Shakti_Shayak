# IP-SAKTI Sahayak

> A multilingual, RAG-based (source-cited) AI assistant for Intellectual Property and regulatory guidance in Ayurveda.

**Smart India Hackathon 2025 — Problem Statement 45**

## Overview

IP-SAKTI Sahayak is a professional decision-support platform that helps Ayurveda practitioners, researchers, startups, MSMEs, and innovators understand the regulatory and intellectual-property pathway for their Ayurveda product or innovation.

**This platform provides informational and decision-support guidance only. It does not constitute legal advice or official regulatory determination.**

## Architecture

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL + pgvector
- **AI Layer:** LLM abstraction (configurable), OpenAI-compatible embeddings

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js >= 20
- Python >= 3.11

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials and API keys
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Run Migrations

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

### 4. Start Backend (Development)

```bash
cd backend
uvicorn app.main:app --reload
```

### 5. Start Frontend (Development)

```bash
cd frontend
npm install
npm run dev
```

## Repository Structure

```
ip-sakti-sahayak/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── ingestion/         # Corpus ingestion scripts (Phase 2)
├── knowledge_base/    # Curated regulatory corpus (Phase 2)
├── evaluation/        # RAG evaluation benchmarks (Phase 8)
├── infrastructure/    # Docker, DB init scripts
└── docs/              # Architecture documentation
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE.md)
- [API Map](docs/API.md)
- [RAG Design](docs/RAG_DESIGN.md)
- [UI Architecture](docs/UI_ARCHITECTURE.md)
- [Development Plan](docs/DEVELOPMENT_PLAN.md)
- [Assumptions & Risks](docs/ASSUMPTIONS.md)

## Development Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Architecture & Planning | ✅ Complete |
| 1 | Scaffolding, DB, Config | 🔄 In Progress |
| 2 | Knowledge Ingestion + Vector Search | ⬜ |
| 3 | RAG + Citation Architecture | ⬜ |
| 4 | Classification + IP/TK/ABS Assessment | ⬜ |
| 5 | Assessment Orchestration + Action Plan | ⬜ |
| 6 | Frontend UX | ⬜ |
| 7 | Multilingual Support | ⬜ |
| 8 | Evaluation + Security + Hardening | ⬜ |
| 9 | Browser-based End-to-End Verification | ⬜ |

## License

Research / Academic Use — SIH 2025
