# ApexRev: Autonomous Enterprise Multi-Agent Intelligence OS

> **High-Yield Autonomous Pipeline & RFP Intelligence Engine**  
> Stateful multi-agent DAG with strict grounding, Model Context Protocol (MCP) tool sandboxes, and Human-in-the-Loop (HITL) checkpoints.

[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-6366f1?style=for-the-badge&logo=github)](https://rajesh2901.github.io/ApexRev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-emerald?style=for-the-badge&logo=python)](https://python.org)

🌐 **Live Hosted Web UI**: [https://rajesh2901.github.io/ApexRev/](https://rajesh2901.github.io/ApexRev/)

---

## ⚡ Quick Start

### 1. Run the Platform & Interactive UI Locally
With `uv` installed, run:
```bash
uv run python main.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser to access the live dashboard, execute autonomous missions, and inspect multi-agent DAG execution.

### 2. Run Test Suite
```bash
uv run python -m tests.test_engine
```

---

## 📐 Architecture Overview

ApexRev utilizes a **Hexagonal Event-Driven State Machine** consisting of 6 decoupled layers:

1. **Client & Presentation**: Real-time obsidian glassmorphic dashboard with streaming reasoning logs and Human-in-the-Loop diff review.
2. **API Gateway & DLP Perimeter**: Authenticated multi-tenant endpoints with PII redaction and rate limiting.
3. **Agent Orchestration**: Stateful DAG pipeline (`Supervisor` → `Research Agent` → `Compliance/RAG Agent` → `Drafting Agent` → `HITL Review Gate` → `Delivery`).
4. **Tool Execution Sandbox**: Model Context Protocol (MCP) microVM connectors for Playwright web scraping, document shredding, and CRM synchronization.
5. **Knowledge Fabric**: Hybrid Search combining dense semantic embeddings with sparse BM25 lexical keyword matching and Reciprocal Rank Fusion (RRF).
6. **Model Gateway & Observability**: Cost-optimized routing (Gemini 2.0 Flash for sub-100ms routing + Claude 3.5 Sonnet / GPT-4o for deep synthesis).

---

## 📁 Repository Structure

```
ApexRev/
├── index.html               # Production dashboard hosted on GitHub Pages
├── main.py                  # Single-command server entrypoint
├── pyproject.toml           # Modern package configuration
├── README.md                # Project documentation & live links
├── src/
│   └── apexrev/
│       ├── __init__.py      # Package metadata
│       ├── state.py         # Agent state dataclasses, node history & checkpoints
│       ├── rag.py           # Hybrid Search Engine (BM25 + Semantic Cosine RRF)
│       ├── tools.py         # MCP tool definitions (Playwright, Doc Shredder, CRM)
│       ├── engine.py        # Multi-Agent State Machine & HITL gate controller
│       └── server.py        # HTTP REST API & static dashboard file server
├── static/
│   └── index.html           # Full enterprise web application UI
└── tests/
    └── test_engine.py       # Unit tests verifying state machine & HITL interruption
```

---

## 🔌 REST API Endpoints

* `POST /api/missions/create`: Initializes a new stateful mission.
* `POST /api/missions/{id}/step`: Executes the next nodes until completion or HITL pause.
* `POST /api/missions/{id}/approve`: Approves the HITL review and triggers external delivery.
* `POST /api/missions/{id}/reject`: Rejects the draft and triggers agent re-planning.
* `GET /api/missions/{id}`: Returns the current state snapshot, node history, and execution logs.
* `GET /api/knowledge`: Lists connected enterprise grounding documents.
* `GET /api/health`: Healthcheck endpoint.

---

## 🌐 GitHub Pages Deployment

The repository includes `index.html` at the root. To enable hosting on GitHub:
1. Navigate to **Repository Settings** > **Pages**.
2. Under **Build and deployment** > **Source**, choose **Deploy from a branch**.
3. Select branch `main` (or `master`) and folder `/ (root)`.
4. Click **Save**. The live dashboard will be hosted at `https://rajesh2901.github.io/ApexRev/`.
