# PayPilot AI

**Autonomous Payment Operations & Enterprise Purchasing Consultant with PayPal Orders v2 Integration**

PayPilot AI is an enterprise procurement engine that bridges natural-language purchasing recommendations with PayPal's payment infrastructure, strictly grounded warehouse catalog inventory, dual-model AI resilience, and an immutable audit ledger.

---

## 1. Problem & Solution

### The Problem
Traditional e-commerce search requires buyers to know exact SKUs, navigate disparate categories, and manually reconcile spending limits. Conversely, generative AI shopping assistants often suffer from hallucinated products, obsolete pricing, phantom stock levels, and fragile payment handoffs vulnerable to price tampering.

### The PayPilot AI Solution
PayPilot AI unifies natural-language procurement with fintech payment integrity:
1. **Catalog Grounding**: The AI model recommendations are strictly mapped to authoritative warehouse catalog SKUs and certified prices.
2. **Dual-Model AI Resilience**: Automatic graceful fallback from `gemini-3.8-flash` to `gemini-3.5-flash-lite` during upstream high demand spikes (HTTP 503/429), accompanied by a deterministic Mock engine for offline evaluation.
3. **Transaction Risk Scoring**: Transparent, multi-factor risk assessment scoring (0–100) evaluating budget variance, SKU validity, order velocity, and quantity constraints.
4. **Server-Enforced PayPal Checkout**: Zero trust in client calculations. Internal orders, PayPal Sandbox Orders v2 creation, and captures are verified server-side with strict idempotency and atomic rollbacks.
5. **Auditable Settlement & PDF Receipts**: Immutable audit event logs and on-demand official PDF receipt generation for completed orders.

---

## 2. Key Features

- **Authoritative Merchant Catalog**: Certified decimal pricing (`Decimal(10, 2)` serialized as exact strings), real-time inventory tracking, instant search, and category filtering (Ergonomics, Technology, Audio, Lighting, Furniture, Accessories).
- **AI Purchasing Consultant**: Natural language procurement interpreter that extracts shopping intent and provides grounded recommendations respecting customer budgets.
- **Dual-Model Resilience & Transparency**: Seamless fallback between primary (`gemini-3.8-flash`) and companion (`gemini-3.5-flash-lite`) models with explicit user disclosure and deterministic Test Mode.
- **Explainable Risk Assessment**: Live pre-checkout risk scoring categorized as `LOW`, `MEDIUM`, or `HIGH` with itemized risk signals and recommended actions.
- **PayPal Orders v2 Integration**: Official `@paypal/react-paypal-js` button integration powered by server-side OAuth caching, client idempotency keys, and verified capture reconciliation.
- **Inventory Movement Ledger**: Transactional inventory deduction with `RESERVE` and `SETTLE` lifecycle ensuring warehouse stock integrity.
- **Official PDF Receipt Generator**: ReportLab-powered downloadable PDF settlement receipts generated exclusively for verified `COMPLETED` transactions.
- **Transaction Audit Ledger**: Complete chronological timeline of audit log events (`ORDER_CREATED`, `PAYPAL_ORDER_CREATED`, `CAPTURE_COMPLETED`, `INVENTORY_DEDUCTED`).

---

## 3. System Architecture

```
                                 [ Browser Client (React 19 + TypeScript) ]
                                          |                     |
                      +-------------------+                     +-------------------+
                      |                                                             |
                      v                                                             v
        [ REST API / V1 Endpoints ]                                   [ PayPal JavaScript SDK ]
        - GET /api/v1/catalog                                         - Client ID Auth
        - POST /api/v1/assistant/plan                                 - Smart Payment Buttons
        - POST /api/v1/orders                                                       |
        - POST /api/v1/orders/{id}/capture                                          |
        - GET /api/v1/orders/{id}/receipt                                           |
                      |                                                             |
                      +-----------------------------+-------------------------------+
                                                    |
                                                    v
                                    [ FastAPI Backend (Python 3.13) ]
                                                    |
             +--------------------+-----------------+--------------------+
             |                    |                                      |
             v                    v                                      v
    [ AI Provider Layer ]  [ PayPal Service ]                 [ Persistence Layer ]
    - Primary: Gemini 3.8  - OAuth Token Caching              - SQLite (aiosqlite)
    - Fallback: Gemini 3.5 - Orders v2 Create / Capture       - SQLAlchemy 2.x
    - Mock: Deterministic  - Server Amount Validation         - Catalog & Inventory Ledger
                           - Double-Capture Lock              - Immutable Audit Logs
                                                              - PDF Receipt Service
```

---

## 4. Technology Stack

### Backend
- **Framework**: Python 3.13, FastAPI 0.115+, Pydantic v2
- **Database & ORM**: SQLite (`paypilot.db`), SQLAlchemy 2.0 (async), `aiosqlite`
- **PDF Engine**: ReportLab 5.1
- **Testing**: Pytest 9.1, `pytest-asyncio`, `respx` (PayPal API mocking)

### Frontend
- **Framework**: React 19, TypeScript, Vite 8.3
- **Styling**: Tailwind CSS (custom PayPal-inspired editorial fintech theme)
- **Payment SDK**: `@paypal/react-paypal-js`
- **Icons & Tooling**: Lucide React, Oxlint

---

## 5. Security & Payment Integrity Safeguards

1. **Anti-Tampering Price Validation**: The frontend never dictates product prices. All subtotal and tax amounts are computed server-side directly from the catalog database.
2. **Double-Capture Prevention**: Orders in `CAPTURING` or `COMPLETED` states reject concurrent capture attempts. Unique database constraints enforce atomic single-capture operations.
3. **Client-Side & Server-Side Idempotency**: Order creation accepts `X-Idempotency-Key` headers; PayPal creation and capture calls use UUID-based idempotency keys to prevent duplicate payments.
4. **Zero Secret Leakage**: `PAYPAL_CLIENT_SECRET` and `GEMINI_API_KEY` are strictly isolated on the backend. Public endpoints expose only public client IDs. All exceptions and error logs pass through sanitization regexes redacting tokens and API keys.
5. **Restricted Receipt Authorization**: Official PDF receipts are strictly blocked for draft, pending, capturing, cancelled, or failed orders (HTTP 400 Bad Request). Only verified `COMPLETED` transactions can produce a settlement receipt.

---

## 6. Setup and Installation

### Prerequisites
- Python 3.13+
- Node.js 18+ and npm
- Windows PowerShell, macOS zsh, or Linux bash

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate a Python virtual environment
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Copy template and fill in your keys (DO NOT commit .env):
cp .env.example .env

# 5. Run automated test suite (76 tests)
pytest

# 6. Start the FastAPI development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory in a separate terminal
cd frontend

# 2. Install dependencies
npm install

# 3. Run linting and production build validation
npm run lint
npm run build

# 4. Start the Vite development server
npm run dev
```

The frontend will start on `http://127.0.0.1:5173` and automatically establish a handshake with the FastAPI backend on port 8000.

---

## 7. Environment Variables Reference

Configure these in `backend/.env` (use `.env.example` as a template):

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `APP_NAME` | Name of the application | `"PayPilot AI"` |
| `APP_ENV` | Application environment | `development` / `production` |
| `HOST` | Bind host address | `127.0.0.1` |
| `PORT` | Backend port | `8000` |
| `CORS_ORIGINS` | Permitted CORS origins | `["http://localhost:5173","http://127.0.0.1:5173"]` |
| `DATABASE_URL` | SQLite async database connection URL | `sqlite+aiosqlite:///./paypilot.db` |
| `PAYPAL_MODE` | PayPal operating mode | `sandbox` |
| `PAYPAL_BASE_URL` | PayPal REST API base URL | `https://api-m.sandbox.paypal.com` |
| `PAYPAL_CLIENT_ID` | PayPal Developer Sandbox App Client ID | *(from PayPal Developer Dashboard)* |
| `PAYPAL_CLIENT_SECRET`| PayPal Developer Sandbox Secret | *(isolated backend secret)* |
| `PAYPAL_CURRENCY` | Operating settlement currency | `USD` |
| `GEMINI_API_KEY` | Google Gemini API Key | *(from Google AI Studio)* |
| `GEMINI_MODEL` | Primary generative AI model | `gemini-3.8-flash` |
| `GEMINI_FALLBACK_MODEL`| Resilient fallback model | `gemini-3.5-flash-lite` |

---

## 8. Verification & Test Suite

### Automated Backend Tests
Run the complete backend test suite:
```powershell
backend\.venv\Scripts\pytest backend\tests
```
**Status: 76 passed (100% green)**
- `test_receipt.py` (5 tests): PDF generation, line item rendering, rejected status handling (400), non-existent orders (404), unit tests.
- `test_assistant.py` (25 tests): Intent parsing, catalog grounding, 503 fallback, 429 quota fallback, non-transient error handling, prompt injection defense, risk scoring.
- `test_orders_api.py` (11 tests): Order creation, price tampering rejection, concurrency locks, cancellation.
- `test_paypal_service.py` (8 tests): OAuth caching, capture validation, amount mismatch detection.
- `test_security_hardening.py` (23 tests): Idempotency constraints, sanitization, secret leakage prevention.
- `test_catalog.py`, `test_health.py`, `test_seeding.py` (4 tests): Storefront endpoints and database seeding.

### Frontend Quality Assurance
```bash
# Run oxlint for static analysis (0 errors)
npm --prefix frontend run lint

# Run TypeScript compilation and Vite production build (0 errors)
npm --prefix frontend run build
```

---

## 9. Product Demonstration & Media Showcase

A comprehensive demonstration suite, high-definition video walkthrough, and promotional gallery are included in [`demo/`](demo/):

### Master Demonstration Video
- **Primary Video Walkthrough**: [`demo/PayPilot_AI_Final_Demo_Refined.mp4`](demo/PayPilot_AI_Final_Demo_Refined.mp4) (112.0 seconds, 1920×1080 Full HD, 30 FPS H.264, 5.76 MB)
  - Features real browser interactions, visible cursor movements, synchronized captions, and clean studio voiceover narration.
- **Closed Captions (Subtitles)**: [`demo/PayPilot_AI_Final_Demo.srt`](demo/PayPilot_AI_Final_Demo.srt) (13 synchronized UTF-8 subtitle cues)
- **Narration Script**: [`demo/PayPilot_AI_Final_Demo_Script.md`](demo/PayPilot_AI_Final_Demo_Script.md)
- **Scene Storyboard**: [`demo/PayPilot_AI_Final_Demo_Storyboard.md`](demo/PayPilot_AI_Final_Demo_Storyboard.md)

### Media Assets & Screenshot Gallery
- **Complete Asset Catalog**: [`demo/MEDIA_ASSET_INDEX.md`](demo/MEDIA_ASSET_INDEX.md)
- **Desktop Screenshots** (`demo/screenshots/`): 8 Full HD captures (1920×1080) covering storefront hero, catalog search, AI purchasing consultant, risk scoring breakdown, checkout drawer with PayPal Smart Buttons, transaction ledger, and official PDF settlement receipt.
- **Mobile Responsive Screenshots** (`demo/screenshots/`): 3 mobile captures (750×1624) verifying mobile navigation, catalog cards, and mobile AI assistant.
- **Promotional Compositions** (`demo/promotional/`): High-resolution presentation graphics (`paypilot-project-cover.png`, `paypilot-feature-showcase.png`, `paypilot-architecture-showcase.png`).

---

## 10. Known Limitations & Hackathon Freeze Notice

- **Sandbox Scope**: PayPal integration operates against the official PayPal Sandbox environment (`api-m.sandbox.paypal.com`). Live production merchant credential swaps require business verification and live app approval.
- **Model Upstream Pressure**: The primary model `gemini-3.8-flash` occasionally encounters upstream capacity spikes (`503 UNAVAILABLE`). The built-in automated resilience fallback immediately routes requests to `gemini-3.5-flash-lite`, ensuring zero user disruption.
- **Submission Freeze**: All code, database schemas, and dependencies are frozen for final hackathon evaluation.
