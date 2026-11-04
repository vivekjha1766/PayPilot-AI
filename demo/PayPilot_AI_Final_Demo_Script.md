# PayPilot AI — Final Product Demonstration Video Script (Video 2.0)

**Title**: PayPilot AI — Interactive Software Demonstration & Architecture Walkthrough  
**Target File**: `demo/PayPilot_AI_Final_Demo.mp4`  
**Subtitle File**: `demo/PayPilot_AI_Final_Demo.srt`  
**Resolution**: 1920 × 1080 (16:9 Full HD)  
**Frame Rate**: 30 FPS  
**Target Duration**: 112.0 seconds (100–120s specification)  
**Visual Style**: Real browser session, visible mouse cursor with click ripples, live UI state changes, syntax-highlighted IDE code overlays, burned-in subtitles, and subtle ambient fintech audio ducked during voiceover.

---

## Complete Scene-by-Scene Script & Synchronized Timeline

### Scene 1: System Overview & Architecture (0:00 – 0:09 | 9.0s)
* **Visual Action**:
  - Live browser at `http://127.0.0.1:5173/`.
  - Contrasting navy/blue pointer moves smoothly from top center to the PayPilot AI logo.
  - Cursor pauses over the live AI status banner: `AI Assistant: Operational (Primary: gemini-3.8-flash | Fallback: gemini-3.5-flash-lite)`.
  - Page scrolls smoothly down to the storefront section.
* **On-Screen Technical Callout**: `SYSTEM ARCHITECTURE | Enterprise Procurement & PayPal Orders v2 Engine`
* **Burned-In Subtitle (0:01 – 0:08)**:
  `"PayPilot AI is an intelligent purchasing platform combining natural-language recommendations with authoritative catalog grounding and secure PayPal payments."`
* **Spoken Narration (starts at 0.8s)**:
  *"Welcome to PayPilot AI, an intelligent procurement platform combining natural-language purchasing recommendations with authoritative catalog grounding and PayPal Orders v2 settlement."*

---

### Scene 2: Product Catalogue & Inventory Validation (0:09 – 0:24 | 15.0s)
* **Visual Action**:
  - Cursor moves to the search input (`input[placeholder*="Search catalog"]`).
  - Cursor clicks with an animated blue ripple.
  - Types `"ergonomic chair"` letter-by-letter (`delay=80ms`), demonstrating real-time responsive filtering.
  - Catalog filters down to `AeroPro Ergonomic Chair`.
  - Cursor moves to the product card, hovering over the certified unit price (`$289.50`) and warehouse stock (`44 units`).
  - Cursor clicks `"Add to Order"` with a visible click ripple.
  - Cursor glides up to the navigation bar, highlighting the cart badge updating from empty to `1` item and `$289.50`.
* **On-Screen Technical Callout**: `CATALOGUE DISCOVERY | Authoritative Server-Side Pricing & Live Stock Validation`
* **Burned-In Subtitles**:
  - `(0:10 – 0:17)`: `"Users explore a live merchant storefront with server-validated pricing and real-time inventory."`
  - `(0:17 – 0:23)`: `"Searching filters the catalog instantly, and adding an item updates the order total in the navigation bar."`
* **Spoken Narration (starts at 9.8s)**:
  *"Users explore a live merchant storefront backed by server-validated pricing and real-time inventory. When we search for an ergonomic chair, the catalog updates instantly. Adding an item immediately updates the order counter in the navigation bar."*

---

### Scene 3: AI Purchasing Consultant Grounded Inference (0:24 – 0:46 | 22.0s)
* **Visual Action**:
  - Page scrolls smoothly back up to the AI Purchasing Consultant panel.
  - Cursor clicks `#assistant-prompt` with a ripple indicator.
  - Types: `"I need an ergonomic chair for back support under $350."`
  - Cursor clicks `#assistant-budget` with a ripple indicator, types `"350"`.
  - Cursor checks `Test Mode (Mock)` to demonstrate deterministic catalog-grounded evaluation.
  - Cursor moves to the `"Consult"` button and clicks (ripple indicator).
  - Real loading spinner appears with `"Evaluating..."` button state.
  - Backend returns structured proposal.
  - Cursor smoothly moves across the Parsed Intent (`"Buyer seeking ergonomic seating for lumbar support within $350"`), the recommended SKU (`CHAIR-ERGO-01`), unit price (`$289.50`), and the transparent Multi-Factor Risk Score (`Low Risk: 12/100`).
* **On-Screen Technical Callout**: `AI PURCHASING CONSULTANT | Grounded Intent Parsing & Explainable Risk Scoring`
* **Burned-In Subtitles**:
  - `(0:25 – 0:34)`: `"Instead of manual comparisons, buyers consult our AI assistant with natural-language requirements."`
  - `(0:34 – 0:45)`: `"The assistant evaluates the prompt against live warehouse stock, verifying budget constraints and computing risk scores."`
* **Spoken Narration (starts at 24.8s)**:
  *"Rather than manually searching, buyers consult our AI assistant. We describe our requirements: an ergonomic chair under $350. The assistant evaluates the prompt against live warehouse inventory, parsing procurement intent, confirming stock, and calculating multi-factor risk scores."*

---

### Scene 4: Behind the AI & Model Resilience (0:46 – 0:61 | 15.0s)
* **Visual Action**:
  - High-definition IDE code inspection view displaying actual repository source files:
    `backend/app/services/ai/gemini_provider.py` and `assistant_service.py`.
  - Syntax-highlighted code view highlights:
    1. `GeminiAIProvider` class initialization and Google GenAI SDK client.
    2. Primary model (`gemini-3.8-flash`) and fallback model (`gemini-3.5-flash-lite`).
    3. `_classify_error` handling transient `503 UNAVAILABLE` and `429` rate limits.
    4. Strict Pydantic JSON schema grounding (`RawLLMPlanResponse`).
  - Architectural callout badge: `"Advisory AI: Recommendations are advisory and never payment-authoritative."`
* **On-Screen Technical Callout**: `GEMINI RESILIENCE LAYER | Multi-Model Failover & Strict Pydantic Grounding`
* **Burned-In Subtitles**:
  - `(0:47 – 0:54)`: `"Behind the scenes, PayPilot's Gemini Provider layer enforces robust multi-model resilience."`
  - `(0:54 – 0:60)`: `"Configured with primary and fallback models, it handles upstream capacity limits with bounded timeouts and error sanitization."`
* **Spoken Narration (starts at 47.0s)**:
  *"Behind the scenes, PayPilot's Gemini Provider layer enforces robust multi-model resilience. Configured with primary and fallback models, it handles upstream demand spikes through bounded timeouts and strict error sanitization, keeping advisory AI safe."*

---

### Scene 5: Purchase Order Drawer & PayPal Checkout (0:61 – 0:78 | 17.0s)
* **Visual Action**:
  - Return to the live application.
  - Cursor glides to the navbar `"Order"` button, clicks (ripple indicator).
  - The `Purchase Order` review drawer slides smoothly in from the right.
  - Cursor clicks `+` to increment quantity to `2`; subtotal instantly recalculates to `$579.00`.
  - Cursor clicks `-` to decrement quantity back to `1`; subtotal returns to `$289.50`.
  - Cursor glides down to the containerized PayPal Sandbox Smart Buttons (`PayPal`, `Debit or Credit Card`).
  - Highlights client-generated idempotency key generation and duplicate-prevention safeguards.
  - Cursor clicks the close button (`X`) to dismiss the drawer.
* **On-Screen Technical Callout**: `PAYPAL ORDERS V2 INTEGRATION | Client Idempotency Keys & Server-Side Verification`
* **Burned-In Subtitles**:
  - `(0:62 – 0:69)`: `"Opening the purchase order drawer reveals itemized totals with live quantity recalculation."`
  - `(0:69 – 0:77)`: `"Containerized PayPal Smart Buttons enable one-click payment, protected by client-generated idempotency keys."`
* **Spoken Narration (starts at 61.8s)**:
  *"Opening the purchase order drawer reveals itemized totals with live quantity adjustments. Below, containerized PayPal Sandbox Smart Buttons enable one-click payment, protected by client-generated idempotency keys and server-side price validation."*

---

### Scene 6: Transaction Ledger & Official PDF Receipt (0:78 – 0:95 | 17.0s)
* **Visual Action**:
  - Cursor moves to the `"History"` button in the navbar, clicks (ripple indicator).
  - The `Transaction Ledger` modal opens showing authoritative audit records.
  - Cursor clicks on the verified completed historical transaction:
    `Order 3d585126...` ($289.50 USD).
  - Order row expands: displays `COMPLETED` badge, PayPal Order ID `6V772492VC732812R`, and PayPal Capture ID `74868969NJ629324C`.
  - Cursor clicks `"Download Official Receipt (PDF)"` with a visible ripple.
  - File genuinely downloads to `demo/downloaded_receipt_3d585126.pdf`.
  - Inset preview highlights the official ReportLab PDF receipt with verification seal and timestamped capture references.
  - Cursor closes modal.
* **On-Screen Technical Callout**: `TRANSACTION INTEGRITY | Immutable Audit Ledger & Downloadable Official Receipts`
* **Burned-In Subtitles**:
  - `(0:79 – 0:86)`: `"Every initiated and captured order is immutably recorded in the transaction ledger."`
  - `(0:86 – 0:94)`: `"We can review PayPal order and capture references, and download an official itemized PDF receipt."`
* **Spoken Narration (starts at 78.8s)**:
  *"Every initiated and captured order is immutably recorded in the transaction ledger. We can inspect our verified historical sandbox transaction, review PayPal order and capture references, and download an official itemized PDF receipt."*

---

### Scene 7: Payment Protection & Reconciliation Engine (0:95 – 1:07 | 12.0s)
* **Visual Action**:
  - IDE code inspection view displaying actual backend implementation:
    `backend/app/services/paypal_service.py` and `backend/app/models/order.py`.
  - Syntax-highlighted blocks showcase:
    1. `capture_order_with_reconciliation`: automated retrieval of order state if network drops.
    2. Atomic SQLite transaction handling with rollback on stock shortage.
    3. Authoritative snapshot item pricing locking to prevent cart tampering.
    4. ReportLab PDF compilation service generating tamper-resistant receipts.
* **On-Screen Technical Callout**: `PAYMENT HARDENING | Atomic Inventory Ledger & Capture Reconciliation`
* **Burned-In Subtitles**:
  - `(0:96 – 1:06)`: `"Our payment architecture guarantees complete settlement integrity with atomic inventory deductions and capture reconciliation."`
* **Spoken Narration (starts at 95.8s)**:
  *"Our payment architecture guarantees complete settlement integrity: atomic inventory ledger deductions, capture reconciliation on network drops, and tamper-proof PDF generation."*

---

### Scene 8: Closing & Brand Mission (1:07 – 1:12 | 5.0s)
* **Visual Action**:
  - Return to the PayPilot application, smoothly crossfading into a full-screen closing card.
  - Large title: **PayPilot AI**
  - Primary Tagline: **"Shop smarter. Decide better. Pay securely."**
  - Supporting Statement: **"AI-powered purchasing. Grounded recommendations. Secure payments."**
  - Architecture pill badges:
    `[Grounded Gemini AI]` `[PayPal Orders v2]` `[Idempotent Workflows]` `[Audit Ledger]` `[PDF Receipts]`
  - Smooth fade to black at 1:12.
* **On-Screen Technical Callout**: `PAYPILOT AI | Next-Generation AI Agent for Modern Enterprise Commerce`
* **Burned-In Subtitles**:
  - `(1:07 – 1:12)`: `"PayPilot AI: Shop smarter, decide better, and pay securely."`
* **Spoken Narration (starts at 107.2s)**:
  *"PayPilot AI: Shop smarter, decide better, and pay securely. Engineered for modern enterprise commerce."*

