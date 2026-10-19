# PayPilot AI

**Autonomous Payment Operations & Purchasing Agent for Online Businesses**

PayPilot AI enables natural language purchase intent extraction, explainable transaction risk evaluation, and verified PayPal Sandbox checkout execution.

---

## Architecture Overview

* **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.x (async), aiosqlite (SQLite).
* **Frontend**: React 19, TypeScript, Vite, Tailwind CSS.
* **Pricing & Security**: Authoritative Decimal pricing serialized as 2-decimal strings (`"289.50"`). Price reconciliation enforced server-side.
* **AI Service Layer**: Abstract `AIService` interface with a deterministic `MockAIService` double for testing and offline development.
* **Payments**: PayPal Sandbox Orders v2 (implemented in Milestone 2).

---

## Directory Structure

```
PayPilot AI/
├── .env.example              # Template configuration variables
├── .gitignore                # Excludes virtual environments, db files, node_modules
├── README.md                 # Setup, startup, and testing documentation
├── backend/
│   ├── .venv/                # Isolated virtual environment
│   ├── requirements.txt      # FastAPI, SQLAlchemy, aiosqlite, greenlet, pytest
│   ├── pyproject.toml        # Pytest & asyncio configuration
│   ├── app/
│   │   ├── main.py           # FastAPI initialization, CORS, lifespan startup
│   │   ├── core/config.py    # Pydantic Settings
│   │   ├── db/
│   │   │   ├── base.py       # DeclarativeBase
│   │   │   ├── session.py    # Async engine & session factory
│   │   │   └── seed.py       # Deterministic office catalog seeding
│   │   ├── models/catalog.py # CatalogItem SQLAlchemy 2.x model
│   │   ├── schemas/catalog.py# Pydantic schema serializing Decimal to string
│   │   ├── services/ai/      # AIService interface & MockAIService double
│   │   └── api/v1/catalog.py # GET /api/v1/catalog endpoint
│   └── tests/
│       ├── conftest.py       # In-memory SQLite fixtures & AsyncClient transport
│       ├── test_health.py    # /health verification test
│       ├── test_catalog.py   # Catalog items & decimal string price format test
│       └── test_seeding.py   # Idempotent seeding behavior test
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx           # Catalog view & status banner
        ├── services/api.ts   # API client with automatic port detection
        ├── components/
        │   ├── Navbar.tsx    # PayPilot header & live backend status indicator
        │   └── CatalogCard.tsx# Office equipment card with SKU and stock
        └── types/catalog.ts  # CatalogItem and HealthStatus interfaces
```

---

## Setup and Startup (Windows PowerShell)

### 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt

# Run automated tests
python -m pytest

# Start FastAPI development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

> **Note on Port Collisions**: If port 8000 is occupied by an existing local service, run uvicorn on port 8001:
> ```powershell
> python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
> ```

---

### 2. Frontend Setup

```powershell
# In a separate PowerShell terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run production build validation
npm run build

# Start development server
npm run dev
```

The frontend will run on `http://127.0.0.1:5173` (or `5174` if 5173 is occupied) and automatically connect to the active PayPilot AI backend.

---

## Verification Endpoints

* **Health Check**: `GET http://127.0.0.1:8000/health` (or `8001`)
  ```json
  {
    "status": "ok",
    "app": "PayPilot AI",
    "environment": "development",
    "version": "1.0.0"
  }
  ```
* **Catalog API**: `GET http://127.0.0.1:8000/api/v1/catalog` (or `8001`)
  Returns 8 seeded office equipment items with authoritative decimal string prices (e.g., `"289.50"`).
* **Interactive API Documentation**: `http://127.0.0.1:8000/docs`

---

## Milestone Roadmap

- [x] **Milestone 1**: Foundation and Catalog (FastAPI, SQLite, Seed Catalog, React + Vite frontend, Pytest suite)
- [ ] **Milestone 2**: Server-Side PayPal Sandbox Integration (OAuth2 token management, Create Order, Server Capture, Live Verification)
- [ ] **Milestone 3**: AI Intent Parsing & Risk Engine (Provider-independent AIService, Gemini integration, Explainable Risk Card)
- [ ] **Milestone 4**: Client Checkout & PayPal JS SDK Integration
- [ ] **Milestone 5**: Full Audit Trail, Receipt Modal & Hackathon Hardening
