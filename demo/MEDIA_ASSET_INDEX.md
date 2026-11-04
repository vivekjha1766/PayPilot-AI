# PayPilot AI — Media Asset Index & Gallery Catalog

This index catalogs the official collection of high-resolution screenshots, promotional graphics, and demonstration media for **PayPilot AI**. All assets are verified against the running application and authoritative database.

---

## 1. Master Video Deliverables

| Asset Name | Resolution | Duration | Format & Audio | Recommended Usage |
| :--- | :--- | :--- | :--- | :--- |
| **[`PayPilot_AI_Final_Demo_Refined.mp4`](file:///c:/Users/jhavi/Desktop/ai_ml_dev/projects/PayPilot%20AI/demo/PayPilot_AI_Final_Demo_Refined.mp4)** | **1920 × 1080** (Full HD) | **112.0s** (`00:01:52.00`) | H.264 / AAC (44.1 kHz, Normalized, Zero Hum) | **Primary Hackathon Submission Video**, Devpost video embed, YouTube showcase. Features ~22% reduced captions and clean studio narration. |
| **[`PayPilot_AI_Final_Demo.mp4`](file:///c:/Users/jhavi/Desktop/ai_ml_dev/projects/PayPilot%20AI/demo/PayPilot_AI_Final_Demo.mp4)** | 1920 × 1080 (Full HD) | 112.0s (`00:01:52.00`) | H.264 / AAC | Unrefined reference demo video with ambient background chords. |
| **[`PayPilot_AI_Final_Demo.srt`](file:///c:/Users/jhavi/Desktop/ai_ml_dev/projects/PayPilot%20AI/demo/PayPilot_AI_Final_Demo.srt)** | SubRip Text Stream | 13 Cues | UTF-8 Plain Text | Closed caption track for video players, YouTube upload, and accessibility compliance. |

---

## 2. Desktop Screenshots (`demo/screenshots/`)

Captured directly from the running frontend (`http://127.0.0.1:5173/`) in Microsoft Edge at 1920 × 1080 native desktop viewport.

| Filename | Resolution | Category | Content Description | Recommended Usage |
| :--- | :--- | :--- | :--- | :--- |
| **`01-homepage-hero.png`** | 1920 × 1080 | Desktop Screenshot | PayPilot AI brand identity, navigation bar, active Gemini status pill (`Primary: gemini-3.8-flash \| Fallback: gemini-3.5-flash-lite`), and value proposition headline. | README hero image, Devpost header, slide deck title slide. |
| **`02-product-catalogue.png`** | 1920 × 1080 | Desktop Screenshot | Product catalog grid displaying category filters (`ALL`, `Furniture`, `Displays`, `Peripherals`), search bar, multiple product cards, certified unit pricing, warehouse stock counts, and "Add to Order" action buttons. | Product feature gallery, e-commerce workflow documentation. |
| **`03-product-search.png`** | 1920 × 1080 | Desktop Screenshot | Real-time catalog search filtering with `"ergonomic chair"` query active, isolating the `AeroPro Ergonomic Chair` card ($250.00 USD, 44 in stock) with active clear button. | Search & discovery feature highlight. |
| **`04-ai-purchasing-assistant.png`** | 1920 × 1080 | Desktop Screenshot | AI Purchasing Consultant interface with natural-language prompt filled (`"I need an ergonomic chair for back support under $350."`), budget constraint (`$350.00`), and completed recommendation proposal. | AI consultant overview, core AI capability demonstration. |
| **`05-ai-recommendation.png`** | 1920 × 1080 | Desktop Screenshot | Detail view of purchasing proposal: Parsed Procurement Intent, recommended SKU `CHAIR-ERGO-01`, price, stock, structured rationale, and Multi-Factor Risk Score badge (`Low Risk: 12/100`) with budget/inventory breakdown. | AI risk & grounding documentation, technical writeups. |
| **`06-cart-checkout.png`** | 1920 × 1080 | Desktop Screenshot | Slide-out `Purchase Order` review drawer with itemized order total ($250.00 + $39.50 tax = $289.50 USD), quantity adjusters, and containerized PayPal Sandbox Smart Buttons (`PayPal`, `Debit or Credit Card`). | Checkout and payment workflow documentation. |
| **`07-transaction-history.png`** | 1920 × 1080 | Desktop Screenshot | `Transaction Ledger` modal displaying historical completed order `3d585126...` ($289.50 USD), `COMPLETED` badge, PayPal Order ID `6V772492VC732812R`, PayPal Capture ID `74868969NJ629324C`, item breakdown, and official receipt download action. | Auditing, security, and transaction compliance sections. |
| **`08-official-receipt.png`** | 1920 × 1080 | Desktop Screenshot | High-definition document view of the genuinely downloaded ReportLab PDF receipt (`downloaded_receipt_3d585126.pdf`) with official PayPilot verification seal, item breakdown, and PayPal capture metadata. | Invoicing, enterprise compliance, and post-purchase proof. |

---

## 3. Responsive Mobile Screenshots (`demo/screenshots/`)

Captured at standard mobile viewport (375 × 812 pt, rendered at 2.0x Retina scale: 750 × 1624 px).

| Filename | Resolution | Category | Content Description | Recommended Usage |
| :--- | :--- | :--- | :--- | :--- |
| **`09-mobile-homepage.png`** | 750 × 1624 | Mobile Screenshot | Mobile-optimized responsive header, compact brand pill, navigation controls, and hero section without horizontal overflow. | Mobile responsiveness showcase, UI/UX audit documentation. |
| **`10-mobile-catalogue.png`** | 750 × 1624 | Mobile Screenshot | Mobile-responsive catalog view with horizontal category chips, compact search bar, and single-column touch-friendly product cards. | Mobile commerce experience presentation. |
| **`11-mobile-ai-assistant.png`** | 750 × 1624 | Mobile Screenshot | Mobile layout of the AI Purchasing Consultant with completed natural-language query and recommendation proposal card. | Mobile AI assistant showcase, multi-device usability proofs. |

---

## 4. Promotional Showcase Graphics (`demo/promotional/`)

High-impact 16:9 Full HD (1920 × 1080) presentation graphics composed from genuine application screenshots and vector technical schematics.

| Filename | Resolution | Category | Content Description | Recommended Usage |
| :--- | :--- | :--- | :--- | :--- |
| **`paypilot-project-cover.png`** | 1920 × 1080 | Promotional Composition | Minimalist fintech project cover: PayPilot brand lockup, official tagline *"Shop smarter. Decide better. Pay securely."*, four key architectural pillars, and an elegant framed desktop application screenshot. | Devpost project thumbnail, GitHub social preview, presentation title slide. |
| **`paypilot-feature-showcase.png`** | 1920 × 1080 | Promotional Composition | Three-panel feature triptych showcasing: (1) Catalog Discovery with server pricing, (2) Grounded AI Consultant with risk scoring, (3) PayPal v2 Settlement with idempotency. | Hackathon project overview slide, LinkedIn/Twitter feature banner. |
| **`paypilot-architecture-showcase.png`** | 1920 × 1080 | Promotional Composition | Comprehensive 4-column system architecture blueprint: (1) Client Layer (React/Vite/PayPal SDK), (2) FastAPI Gateway (Pydantic v2/Async), (3) AI Resilience Layer (Gemini 3.8/3.5/Mock), (4) Payment Integrity (PayPal Orders v2/SQLite Ledger/ReportLab). | Technical evaluation panel, engineering deep-dive, architecture documentation. |

---

## 5. Verification & Preservation Status

- **Authoritative Database**: `backend/paypilot.db` remains 100% untouched (**exactly 5 historical orders**).
- **Target Completed Order**: `3d585126...` ($289.50 USD, `COMPLETED`, PayPal Order `6V772492VC732812R`, Capture `74868969NJ629324C`) verified intact.
- **Stock Integrity**: `CHAIR-ERGO-01` warehouse stock remains untouched at **`44`**.
- **Payment Safeguards**: **ZERO** new PayPal orders, payments, or sandbox captures were created.
- **Secrets & Privacy**: No `.env` contents, API keys, client secrets, or private tokens are displayed in any image or video frame.

