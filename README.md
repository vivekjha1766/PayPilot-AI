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

## 6. Judge Quick Start & Evaluation Guide

This guide provides end-to-end instructions for hackathon judges and evaluators to run, interact with, and verify PayPilot AI locally.

> [!IMPORTANT]
> **Fintech Environment Safeguards**:
> - **PayPal Sandbox Only**: This application connects exclusively to the official PayPal Developer Sandbox (`api-m.sandbox.paypal.com`). It does **not** process live payments.
> - **Zero Bundled Secrets**: In accordance with open-source security best practices, no real PayPal API credentials or Google Gemini keys are committed to this repository. Evaluators configure their own free sandbox credentials or test using the offline Mock AI provider.
> - **Advisory AI Architecture**: The AI Purchasing Consultant is strictly **advisory**. Recommendations are grounded against the database, but all payment totals, tax amounts, inventory reservations, and captures are enforced server-side by FastAPI and SQLite.

---

### Step 1: Prerequisites & Supported Software

Verify that your workstation meets the following runtime requirements:
- **Python**: Version `3.11`, `3.12`, or `3.13` (`python --version`)
- **Node.js**: Version `18.x`, `20.x`, or `22.x` (`node --version`)
- **Package Managers**: `pip` (Python) and `npm` (Node)
- **Supported Operating Systems**: Windows (PowerShell / Command Prompt), macOS (zsh / bash), or Linux (bash)

---

### Step 2: Backend Installation & Automatic Database Initialization

The backend is built with FastAPI and SQLite (`aiosqlite`). On initial startup, the backend automatically initializes `backend/paypilot.db`, creates all required tables, applies schema migrations, and seeds the 8-item catalog with certified pricing and stock. No manual database setup scripts are required.

```bash
# 1. From the repository root, enter the backend directory
cd backend

# 2. Create an isolated Python virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. Create local environment file from template
# Windows PowerShell / Linux / macOS:
cp .env.example .env
```

---

### Step 3: Configure Environment & Credentials

Open `backend/.env` in your editor. Below is the configuration reference:

```env
APP_NAME="PayPilot AI"
APP_ENV=development
HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174","http://127.0.0.1:5174"]
DATABASE_URL=sqlite+aiosqlite:///./paypilot.db

# --- PayPal Sandbox (Required for Live Sandbox Checkout) ---
PAYPAL_MODE=sandbox
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_CURRENCY=USD

# --- Gemini AI (Optional - Test Mode Available Offline) ---
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODEL=gemini-3.5-flash-lite
```

#### A. Obtaining PayPal Sandbox Credentials (Free)
1. Log in to the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/).
2. Navigate to **Apps & Credentials** > **Sandbox**.
3. Create an application (or use the **Default Application**) and copy the **Client ID** and **SecretKey**.
4. Paste them into `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` in `backend/.env`.
5. Under **Testing Tools** > **Sandbox Accounts**, note the generated **Personal Buyer Account** email and password for completing test checkouts.

#### B. Gemini API Key (Optional — Offline Deterministic Mock Included)
- **Live Mode**: Obtain a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and paste it into `GEMINI_API_KEY`.
- **Offline / Mock Mode**: If `GEMINI_API_KEY` is left blank, the application automatically defaults to the deterministic `MockAIProvider`. Evaluators can also check the **"Test Mode (Mock)"** toggle in the UI at any time to run the purchasing consultant without network calls.

---

### Step 4: Start the Backend Service

```bash
# Start FastAPI backend on 127.0.0.1:8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
You should see:
```text
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```
- Health Check: `http://127.0.0.1:8000/health`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

---

### Step 5: Frontend Installation & Startup

In a **separate terminal**, set up and run the React + Vite frontend:

```bash
# 1. From repository root, navigate to frontend
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start the Vite development server
npm run dev
```

The frontend will start on `http://127.0.0.1:5173`. Open this URL in Microsoft Edge, Google Chrome, Safari, or Mozilla Firefox.

---

## 7. Interactive Judge Evaluation Walkthrough

Follow these sequential steps to evaluate all core features of PayPilot AI:

### A. Catalog Exploration & Instant Search
1. Open `http://127.0.0.1:5173/` in your browser.
2. Filter items using the category chips: `ALL`, `Furniture`, `Displays`, `Peripherals`, `Audio`, `Lighting`, `Accessories`.
3. Type `"ergonomic chair"` in the search bar. Observe instant real-time filtering isolating the *AeroPro Ergonomic Mesh Chair* ($289.50 USD) with active stock counter.
4. Click **Clear** to restore the catalog.

### B. AI Purchasing Consultant & Risk Scoring
1. Scroll to the **Purchasing Consultant** section.
2. Choose one of the sample prompt pills (e.g., *"Equip an ergonomic workstation with a chair and split keyboard under $500"*), or enter your own procurement query.
3. Set an optional target budget (e.g., `500.00`).
4. Click **Generate Purchase Proposal**.
   - If using live Gemini: Intent is analyzed with `gemini-3.8-flash` (with automatic fallback to `gemini-3.5-flash-lite` if upstream limits are reached).
   - If offline or toggled: The deterministic Mock engine interprets SKUs instantly.
5. Review the **Grounded Proposal**:
   - Parsed Procurement Intent and SKU mapping.
   - Grounded warehouse stock check.
   - **Explainable Multi-Factor Risk Score** (`LOW`, `MEDIUM`, or `HIGH`) evaluating price delta, quantity constraints, and order velocity.
6. Click **Add Proposal to Order** to automatically stage recommended items into your cart.

### C. PayPal Sandbox Checkout & Server-Side Capture
1. Click **Purchase Order** (top-right cart button) to open the slide-out checkout drawer.
2. Review line items, quantity selectors, subtotal, and calculated tax.
3. If valid sandbox credentials were provided in `backend/.env`, official containerized **PayPal Smart Buttons** appear.
4. Click the yellow **PayPal** button. A secure PayPal Sandbox popup opens.
5. Log in with your Sandbox Personal Buyer account credentials.
6. Click **Complete Purchase** on the PayPal modal.
7. **What happens behind the scenes**:
   - The frontend calls `POST /api/v1/orders` with an `X-Idempotency-Key`.
   - The FastAPI backend validates catalog prices server-side, checks available stock, and creates a PayPal Sandbox order.
   - Upon buyer approval, `POST /api/v1/orders/{id}/capture` executes server-side amount verification, commits atomic inventory deduction in the movement ledger, and marks the internal order `COMPLETED`.

### D. Transaction History & Audit Trail
1. Click **History** in the top navigation bar to open the **Transaction Ledger** modal.
2. Observe all historical orders, status badges (`COMPLETED`, `CANCELLED`), order timestamps, and total settlement amounts.
3. Click an order card to expand its complete server-side audit trail:
   - `ORDER_CREATED`
   - `PAYPAL_ORDER_CREATED`
   - `CAPTURE_COMPLETED`
   - `INVENTORY_DEDUCTED`

### E. Official PDF Settlement Receipt Verification
1. Inside the Transaction Ledger modal, click **Download Receipt** on any verified `COMPLETED` order.
2. The browser downloads an official PDF receipt generated on-demand by ReportLab (`downloaded_receipt_<order_id>.pdf`).
3. Open the receipt to inspect:
   - Official PayPilot verification seal and merchant metadata.
   - Unique order UUID and PayPal Capture Transaction ID.
   - Itemized table with certified unit prices and tax calculation.
   - Cryptographic settlement verification footer.
4. *Security note*: Attempting to request a receipt for uncaptured or cancelled orders returns an intentional `HTTP 400 Bad Request`.

---

## 8. Verification & Automated Test Suites

### Automated Backend Tests (76 Tests, 100% Pass)
To execute the complete automated test suite covering all payment, AI, and security logic:

```powershell
# From repository root
backend\.venv\Scripts\pytest backend\tests -v
```
Test suite breakdown:
- `backend/tests/test_assistant.py` (25 tests): Intent parsing, catalog grounding, 503 fallback, 429 quota fallback, non-transient error handling, prompt injection defense, risk scoring.
- `backend/tests/test_receipt.py` (5 tests): PDF generation, line item rendering, rejected status handling (400), non-existent orders (404), layout formatting.
- `backend/tests/test_orders_api.py` (11 tests): Order creation, price tampering rejection, concurrency locks, cancellation.
- `backend/tests/test_paypal_service.py` (8 tests): OAuth caching, capture validation, amount mismatch detection.
- `backend/tests/test_security_hardening.py` (23 tests): Idempotency constraints, sanitization, secret leakage prevention.
- `backend/tests/test_catalog.py`, `test_health.py`, `test_seeding.py` (4 tests): Storefront endpoints, database seeding, health routes.

### Frontend Quality Assurance & Production Build
```bash
# Oxlint static analysis (0 errors)
npm --prefix frontend run lint

# TypeScript compilation & Vite production build (0 errors)
npm --prefix frontend run build
```

---

## 9. Troubleshooting Common Issues

| Issue / Symptom | Probable Cause | Recommended Resolution |
| :--- | :--- | :--- |
| **Backend fails with `ModuleNotFoundError: No module named 'aiosqlite'`** | Running against global Python instead of virtual environment | Activate the virtual environment (`.\.venv\Scripts\Activate.ps1` or `source .venv/bin/activate`) before running `uvicorn` or `pytest`. |
| **Port 8000 already in use** | An earlier backend server instance is running | Terminate the existing process or run Uvicorn on an alternate port: `uvicorn app.main:app --port 8001` (and update `CORS_ORIGINS`). |
| **Frontend shows "PayPal client configuration unavailable"** | `PAYPAL_CLIENT_ID` is empty or missing in `backend/.env` | Add your sandbox client ID to `backend/.env` and restart the backend. Direct catalog exploration and AI proposals remain fully functional without PayPal keys. |
| **PayPal button popup shows generic error or closes** | Sandbox buyer account login mismatch | Ensure you are logging into the popup using a **Sandbox Personal Account** generated in your PayPal Developer dashboard, not real PayPal credentials. |
| **AI Assistant displays "Gemini AI provider is not configured"** | `GEMINI_API_KEY` was left blank in `backend/.env` | Check the **"Test Mode (Mock)"** checkbox in the top-right of the Purchasing Consultant card to evaluate full recommendations offline. |
| **CORS network error in browser console** | Frontend origin not present in backend CORS list | Ensure `backend/.env` contains `CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]`. |

---

## 10. Product Demonstration & Media Showcase

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

## 11. Known Limitations & Hackathon Freeze Notice

- **Sandbox Scope**: PayPal integration operates against the official PayPal Sandbox environment (`api-m.sandbox.paypal.com`). Live production merchant credential swaps require business verification and live app approval.
- **Model Upstream Pressure**: The primary model `gemini-3.8-flash` occasionally encounters upstream capacity spikes (`503 UNAVAILABLE`). The built-in automated resilience fallback immediately routes requests to `gemini-3.5-flash-lite`, ensuring zero user disruption.
- **Submission Freeze**: All code, database schemas, and dependencies are frozen for final hackathon evaluation.

---

## 12. License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for complete details.

```text
Copyright (c) 2026 Vivek Jha
SPDX-License-Identifier: MIT
```
