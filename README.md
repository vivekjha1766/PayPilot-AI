# PayPilot AI

**Autonomous Payment Operations & Purchasing Agent for Online Businesses**

PayPilot AI enables natural language purchase intent extraction, explainable transaction risk evaluation, and verified PayPal Sandbox checkout execution.

---

## Architecture Overview

* **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.x (async), aiosqlite (SQLite).
* **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, `@paypal/react-paypal-js`.
* **Pricing & Security**: Authoritative Decimal pricing serialized as 2-decimal strings (`"289.50"`). Price reconciliation enforced server-side.
* **Payments**: PayPal Sandbox Orders v2 REST API (OAuth token caching, server order creation, server capture with amount and currency verification, idempotency, and reconciliation).
* **AI Service Layer**: Abstract `AIService` interface with a deterministic `MockAIService` double for testing and offline development (Milestone 3).

---

## Directory Structure

```
PayPilot AI/
├── .env.example                  # Template configuration variables
├── .gitignore                    # Excludes virtual environments, db files, node_modules
├── README.md                     # Setup, startup, and testing documentation
├── backend/
│   ├── .venv/                    # Isolated virtual environment
│   ├── requirements.txt          # FastAPI, SQLAlchemy, aiosqlite, respx, pytest
│   ├── pyproject.toml            # Pytest & asyncio configuration
│   ├── scripts/
│   │   └── verify_live_sandbox.py# Script for testing live sandbox credentials
│   ├── app/
│   │   ├── main.py               # FastAPI initialization, CORS, lifespan startup
│   │   ├── core/config.py        # Pydantic Settings
│   │   ├── db/
│   │   │   ├── base.py           # DeclarativeBase
│   │   │   ├── session.py        # Async engine & session factory
│   │   │   └── seed.py           # Deterministic office catalog seeding
│   │   ├── models/
│   │   │   ├── catalog.py        # CatalogItem SQLAlchemy 2.x model
│   │   │   └── order.py          # Order, OrderItem, and AuditLog models
│   │   ├── schemas/
│   │   │   ├── catalog.py        # Pydantic schema serializing Decimal to string
│   │   │   └── order.py          # Order, Item, Capture, and PaymentConfig schemas
│   │   ├── services/
│   │   │   ├── paypal_service.py # PayPal Orders v2 OAuth, Create, Capture, Reconcile
│   │   │   └── ai/               # AIService interface & MockAIService double
│   │   └── api/v1/
│   │       ├── router.py         # v1 router aggregator
│   │       ├── catalog.py        # GET /api/v1/catalog endpoint
│   │       ├── payments.py       # GET /api/v1/payments/config (public client ID)
│   │       └── orders.py         # POST /orders, POST /orders/{id}/capture, /cancel
│   └── tests/
│       ├── conftest.py           # In-memory SQLite fixtures & AsyncClient transport
│       ├── test_health.py        # /health verification test
│       ├── test_catalog.py       # Catalog items & decimal string price format test
│       ├── test_seeding.py       # Idempotent seeding behavior test
│       ├── test_paypal_service.py# PayPal service unit tests (OAuth, capture, mismatch, timeout)
│       └── test_orders_api.py    # Order creation, price tampering, capture, concurrency, cancellation
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx               # Catalog view, cart drawer, and receipt modal
        ├── services/api.ts       # API client with auto-detection for ports 8000/8001
        ├── components/
        │   ├── Navbar.tsx        # PayPilot header, status indicator & cart trigger
        │   ├── CatalogCard.tsx   # Product card with "+ Add to Order" button
        │   ├── CheckoutDrawer.tsx# Cart slide-over with PayPalButtons wrapper
        │   ├── PayPalButtonWrapper.tsx # Real @paypal/react-paypal-js integration
        │   └── ReceiptModal.tsx  # Verified PayPal transaction receipt
        └── types/
            ├── catalog.ts        # CatalogItem and HealthStatus interfaces
            └── order.ts          # Order, Item, Cart, and CaptureResult interfaces
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

# Run automated tests (all 22 passing)
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

## API Endpoints (Milestone 2)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check endpoint returning app name and version. |
| `GET` | `/api/v1/catalog` | Authoritative database catalog items with Decimal prices. |
| `GET` | `/api/v1/payments/config` | Returns public PayPal Client ID and currency. **Never returns secret.** |
| `POST` | `/api/v1/orders` | Creates internal order + PayPal sandbox order. Validates stock and calculates totals server-side. |
| `GET` | `/api/v1/orders/{id}` | Retrieves internal order details, items, and audit history. |
| `POST` | `/api/v1/orders/{id}/capture` | Captures authorized PayPal sandbox payment, validates amounts, deducts stock, and marks COMPLETED. |
| `POST` | `/api/v1/orders/{id}/cancel` | Marks order as CANCELLED upon buyer cancellation callback. |

---

## Live Sandbox Verification

To test with your live PayPal Developer sandbox credentials:

1. Copy `.env.example` to `backend/.env`.
2. Add your sandbox merchant credentials:
   ```env
   PAYPAL_CLIENT_ID=your_sandbox_client_id
   PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
   PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
   PAYPAL_CURRENCY=USD
   ```
3. Run the verification script:
   ```powershell
   python backend/scripts/verify_live_sandbox.py
   ```

---

## Milestone Roadmap

- [x] **Milestone 1**: Foundation and Catalog (FastAPI, SQLite, Seed Catalog, React + Vite frontend, Pytest suite)
- [x] **Milestone 2**: Real PayPal Sandbox Checkout (PayPal Orders v2 REST API, `@paypal/react-paypal-js`, server capture, price reconciliation, idempotency)
- [ ] **Milestone 3**: AI Intent Parsing & Risk Engine (Provider-independent AIService, Gemini integration, Explainable Risk Card)
- [ ] **Milestone 4**: Interactive Natural Language Purchasing Dashboard
- [ ] **Milestone 5**: Full Audit Trail, Receipt Modal & Hackathon Hardening
