# PayPilot AI — Product Demonstration Video Storyboard (Video 2.0)

**Project**: PayPilot AI — Hackathon Software Demonstration  
**Master Video**: `demo/PayPilot_AI_Final_Demo.mp4`  
**Duration**: 112.0 seconds (3,360 frames @ 30 FPS)  
**Viewport**: 1920 × 1080 (16:9 Full HD)  
**Design Palette**:
- Deep Navy: `#102a43`
- Brand Blue: `#0070e0`
- Cyan Accent: `#00c8ff`
- Pure White: `#ffffff`
- Surface Muted: `#f0f4f8`

---

## Visual & Technical Storyboard

### Scene 1: System Overview & Architecture (0.0s – 9.0s | Frames 0 – 270)
* **Framing & Viewport**: Desktop browser 1920x1080, top hero view.
* **Cursor Motion**: (960, 100) → moves smoothly in 30 steps to logo at (140, 48), pauses for 1.0s, moves to Status Pill at (780, 48), pauses for 1.2s.
* **Camera / Scroll**: Smooth programmatic scroll from top=0 to top=480 at 6.0s.
* **Key Visuals**:
  - PayPilot AI navigation bar and hero headline.
  - Active Gemini status badge showing `Primary: gemini-3.8-flash | Fallback: gemini-3.5-flash-lite`.
* **Lower-Third Overlay**:
  - Category: `SYSTEM ARCHITECTURE`
  - Title: `Enterprise Procurement & PayPal Orders v2 Engine`
* **Synchronized Subtitle**:
  `"PayPilot AI is an intelligent purchasing platform combining natural-language recommendations with authoritative catalog grounding and secure PayPal payments."`

---

### Scene 2: Product Catalogue & Inventory Validation (9.0s – 24.0s | Frames 270 – 720)
* **Framing & Viewport**: Catalog grid view showing category pills, search bar, and item cards.
* **Cursor Motion**:
  - Frame 280: Cursor moves from (780, 48) to search input at (1350, 490).
  - Frame 320: Cursor clicks with animated circular blue ripple (`.demo-click-ripple`).
  - Frame 340–440: Virtual keyboard types `"ergonomic chair"` with typing delay; items filter dynamically.
  - Frame 470: Cursor moves to `AeroPro Ergonomic Chair` card, hovers over unit price `$289.50` and stock `44 units`.
  - Frame 530: Cursor moves to `"Add to Order"` button on the card, clicks (ripple animation).
  - Frame 570–650: Cursor glides up to the navbar Cart button at (1760, 48), hovering over the cart badge updating to `1` item / `$289.50`.
* **Lower-Third Overlay**:
  - Category: `CATALOGUE DISCOVERY`
  - Title: `Authoritative Server-Side Pricing & Live Stock Validation`
* **Synchronized Subtitles**:
  - `(9.0s – 17.0s)`: `"Users explore a live merchant storefront with server-validated pricing and real-time inventory."`
  - `(17.0s – 24.0s)`: `"Searching filters the catalog instantly, and adding an item updates the order total in the navigation bar."`

---

### Scene 3: AI Purchasing Consultant Grounded Inference (24.0s – 46.0s | Frames 720 – 1380)
* **Framing & Viewport**: AI Purchasing Consultant panel, top=80.
* **Cursor Motion**:
  - Frame 730: Page scrolls smoothly up to AI panel.
  - Frame 760: Cursor clicks prompt input `#assistant-prompt` (ripple).
  - Frame 780–860: Types: `"I need an ergonomic chair for back support under $350."`
  - Frame 880: Cursor clicks `#assistant-budget` (ripple), types `"350"`.
  - Frame 920: Cursor clicks `Test Mode (Mock)` toggle to guarantee instant deterministic demonstration.
  - Frame 960: Cursor clicks `"Consult"` button (ripple).
  - Frame 970–1030: Loading spinner appears with `"Evaluating..."` button text.
  - Frame 1040: Purchasing proposal renders.
  - Frame 1060–1200: Cursor smoothly tracks across:
    1. `Parsed Procurement Intent`: `"Buyer seeking ergonomic seating for lumbar support within $350"`
    2. Resilience Engine Badge: `Mock Engine / Grounded`
    3. Recommended Item Card: `AeroPro Ergonomic Chair` (`CHAIR-ERGO-01`), unit price `$289.50`, stock `44`
    4. Multi-Factor Risk Score: `Low Risk: 12/100` (Budget Risk 0, Inventory Risk 12)
* **Lower-Third Overlay**:
  - Category: `AI PURCHASING CONSULTANT`
  - Title: `Grounded Intent Parsing & Explainable Risk Scoring`
* **Synchronized Subtitles**:
  - `(25.0s – 34.0s)`: `"Instead of manual comparisons, buyers consult our AI assistant with natural-language requirements."`
  - `(34.0s – 46.0s)`: `"The assistant evaluates the prompt against live warehouse stock, verifying budget constraints and computing risk scores."`

---

### Scene 4: Behind the AI & Model Resilience (46.0s – 61.0s | Frames 1380 – 1830)
* **Framing & Viewport**: High-definition split-screen IDE code inspection.
* **Layout**:
  - Dark slate IDE frame (`#101924`) with macOS/VS Code-style header tabs.
  - Left pane: `backend/app/services/ai/gemini_provider.py`
  - Highlighted code blocks:
    * `class GeminiAIProvider(BaseAIProvider)`
    * `primary_model = settings.gemini_model` (`gemini-3.8-flash`)
    * `fallback_model = settings.gemini_fallback_model` (`gemini-3.5-flash-lite`)
    * `_classify_error` handling transient `503 UNAVAILABLE` and timeouts
  - Right pane: Architectural schematic showing failover pipeline and advisory boundary.
* **Lower-Third Overlay**:
  - Category: `GEMINI RESILIENCE LAYER`
  - Title: `Multi-Model Failover & Strict Pydantic Grounding`
* **Synchronized Subtitles**:
  - `(47.0s – 54.0s)`: `"Behind the scenes, PayPilot's Gemini Provider layer enforces robust multi-model resilience."`
  - `(54.0s – 61.0s)`: `"Configured with primary and fallback models, it handles upstream capacity limits with bounded timeouts and error sanitization."`

---

### Scene 5: Purchase Order Drawer & PayPal Checkout (61.0s – 78.0s | Frames 1830 – 2340)
* **Framing & Viewport**: Live application with sliding `Purchase Order` drawer from right.
* **Cursor Motion**:
  - Frame 1840: Returns to browser. Cursor glides to navbar `"Order"` button, clicks (ripple).
  - Frame 1880: `Purchase Order` drawer slides in.
  - Frame 1920: Cursor clicks `+` quantity button (ripple). Quantity becomes `2`, subtotal updates to `$579.00`.
  - Frame 1980: Cursor clicks `-` quantity button (ripple). Quantity returns to `1`, subtotal returns to `$289.50`.
  - Frame 2040–2180: Cursor hovers over containerized PayPal Sandbox Smart Buttons (`PayPal`, `Debit or Credit Card`).
  - Frame 2220: Cursor clicks drawer close button (`X`) (ripple). Drawer slides shut.
* **Lower-Third Overlay**:
  - Category: `PAYPAL ORDERS V2 INTEGRATION`
  - Title: `Client Idempotency Keys & Server-Side Verification`
* **Synchronized Subtitles**:
  - `(62.0s – 69.0s)`: `"Opening the purchase order drawer reveals itemized totals with live quantity recalculation."`
  - `(69.0s – 78.0s)`: `"Containerized PayPal Smart Buttons enable one-click payment, protected by client-generated idempotency keys."`

---

### Scene 6: Transaction Ledger & Official PDF Receipt (78.0s – 95.0s | Frames 2340 – 2850)
* **Framing & Viewport**: `Transaction Ledger` modal centered over application canvas.
* **Cursor Motion**:
  - Frame 2350: Cursor glides to navbar `"History"` button, clicks (ripple).
  - Frame 2380: Modal opens.
  - Frame 2410: Cursor moves to completed order row `Order 3d585126...` ($289.50 USD), clicks (ripple).
  - Frame 2430–2520: Order expands; highlights `COMPLETED` status, PayPal Order ID `6V772492VC732812R` and Capture ID `74868969NJ629324C`.
  - Frame 2540: Cursor clicks `"Download Official Receipt (PDF)"` (ripple).
  - Frame 2560: File genuinely downloads (`downloaded_receipt_3d585126.pdf`).
  - Frame 2580–2750: Rendered receipt inset displays official ReportLab PDF with security watermark, itemized breakdown, and capture metadata.
  - Frame 2780: Cursor clicks modal close button (`X`) (ripple).
* **Lower-Third Overlay**:
  - Category: `TRANSACTION INTEGRITY`
  - Title: `Immutable Audit Ledger & Downloadable Official Receipts`
* **Synchronized Subtitles**:
  - `(79.0s – 86.0s)`: `"Every initiated and captured order is immutably recorded in the transaction ledger."`
  - `(86.0s – 95.0s)`: `"We can review PayPal order and capture references, and download an official itemized PDF receipt."`

---

### Scene 7: Payment Protection & Reconciliation Engine (95.0s – 107.0s | Frames 2850 – 3210)
* **Framing & Viewport**: IDE code inspection view of payment security services.
* **Layout**:
  - Dark IDE window displaying `backend/app/services/paypal_service.py` and `backend/app/models/order.py`.
  - Highlighted code blocks:
    * Atomic inventory reservation ledger with rollback on shortage.
    * Client idempotency key caching preventing duplicate charges.
    * Automated capture reconciliation for network dropouts.
    * PDF receipt generator with ReportLab canvas.
* **Lower-Third Overlay**:
  - Category: `PAYMENT HARDENING`
  - Title: `Atomic Inventory Ledger & Capture Reconciliation`
* **Synchronized Subtitle**:
  `"Our payment architecture guarantees complete settlement integrity: atomic inventory ledger deductions, capture reconciliation on network drops, and tamper-proof PDF generation."`

---

### Scene 8: Closing & Brand Mission (107.0s – 112.0s | Frames 3210 – 3360)
* **Framing & Viewport**: Full-screen branded closing card.
* **Layout**:
  - Deep Navy background (`#102a43`) with subtle cyan border framing.
  - Large Brand Title: `PayPilot AI`
  - Primary Tagline: `"Shop smarter. Decide better. Pay securely."`
  - Supporting Statement: `"AI-powered purchasing. Grounded recommendations. Secure payments."`
  - Technical badges: `[Grounded Gemini AI]` `[PayPal Orders v2]` `[Idempotent Workflows]` `[Audit Ledger]` `[PDF Receipts]`
  - Smooth fade to black from frame 3300 to 3360 (110.0s – 112.0s).
* **Lower-Third Overlay**:
  - Category: `PAYPILOT AI`
  - Title: `Next-Generation AI Agent for Modern Enterprise Commerce`
* **Synchronized Subtitle**:
  `"PayPilot AI: Shop smarter, decide better, and pay securely. Engineered for modern enterprise commerce."`

