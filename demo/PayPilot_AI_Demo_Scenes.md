# PayPilot AI — Demonstration Scene Plan & Storyboard

This document specifies the exact visual composition, timing, and on-screen elements for `demo/PayPilot_AI_Demo.mp4`.

---

## Storyboard Architecture

```
+-----------------------------------------------------------------------------------+
| [0:00 - 0:09] Scene 1: Brand Introduction & Enterprise Architecture               |
| Navy Editorial Card | Brand Identity (#0070E0) | Stack Specifications             |
+-----------------------------------------------------------------------------------+
                                          | (0.5s Crossfade)
                                          v
+-----------------------------------------------------------------------------------+
| [0:09 - 0:18] Scene 2: Live Storefront & Authoritative Inventory                  |
| Desktop Browser View | Certified Stock Levels | Active FastAPI Backend Status     |
+-----------------------------------------------------------------------------------+
                                          | (0.5s Crossfade)
                                          v
+-----------------------------------------------------------------------------------+
| [0:18 - 0:26] Scene 3: Catalog Discovery & Category Filtering                     |
| Ergonomics Category Active | Real-Time Pricing | Sub-Second Responsiveness        |
+-----------------------------------------------------------------------------------+
                                          | (0.5s Crossfade)
                                          v
+-----------------------------------------------------------------------------------+
| [0:26 - 0:36] Scene 4: AI Purchasing Consultant                                   |
| Natural Language Prompt | $500 Budget Setting | Grounded Catalog Intent           |
+-----------------------------------------------------------------------------------+
                                          | (0.5s Crossfade)
                                          v
+-----------------------------------------------------------------------------------+
| [0:36 - 0:46] Scene 5: Dual-Model Gemini Resilience & Risk Scoring                |
| Fallback Model Badge | Within-Budget Proposal | LOW RISK (15/100) Assessment      |
+-----------------------------------------------------------------------------------+
                                          | (0.5s Crossfade)
                                          v
+-----------------------------------------------------------------------------------+
| [0:46 - 0:55] Scene 6: Cart & PayPal Orders v2 Checkout Drawer                    |
| Itemized Snapshot | Client Idempotency Keys | Official PayPal Sandbox SDK Button  |
+-----------------------------------------------------------------------------------+
                                          | (0.5s Crossfade)
                                          v
+-----------------------------------------------------------------------------------+
| [0:55 - 1:05] Scene 7: Transaction Ledger & Official PDF Receipt                  |
| 5 Preserved Transactions | Order 3d585126 | Download Official Receipt (PDF) Action|
+-----------------------------------------------------------------------------------+
                                          | (0.5s Crossfade)
                                          v
+-----------------------------------------------------------------------------------+
| [1:05 - 1:13] Scene 8: Security Safeguards & Submission Freeze                    |
| 76 Passing Tests | Zero Secret Leakage | Final Hackathon Submission Freeze        |
+-----------------------------------------------------------------------------------+
```

---

## Detailed Scene Specifications

### Scene 1: Title Card & Brand Introduction
- **Time Range**: 0:00 – 0:09 (270 frames)
- **Background**: Deep Fintech Navy (`#102A43`)
- **Primary Typography**: Modern Serif / Clean Sans-Serif
- **Badge Chips**: `FastAPI` • `React 19` • `TypeScript` • `SQLAlchemy 2.x` • `Google Gemini` • `PayPal Orders v2`
- **Sub-Title**: *Enterprise Purchasing Intelligence with Server-Side Payment Integrity*
- **Caption**: `PayPilot AI | Enterprise Procurement & PayPal Orders v2 Engine`

### Scene 2: Live Storefront & Catalog
- **Time Range**: 0:09 – 0:18 (270 frames)
- **Source**: Headless browser render (`http://127.0.0.1:5173/`)
- **Key Elements**:
  - Live status indicator: `API Connected (http://127.0.0.1:8000)`
  - Active products: `CHAIR-ERGO-01`, `DESK-STAND-01`, `MON-CURVE-01`
  - Real-time warehouse inventory counters
- **Caption**: `Authoritative Storefront | Real-Time Stock & Certified Unit Pricing`

### Scene 3: Catalog Filtering & Discovery
- **Time Range**: 0:18 – 0:26 (240 frames)
- **Source**: Headless browser render (`http://127.0.0.1:5173/?category=Ergonomics`)
- **Key Elements**:
  - Active category tab: `Ergonomics` (Brand Blue `#0070E0`)
  - Filtered items: Ergonomic chairs and adjustable desks
  - Clear search query support
- **Caption**: `Catalog Discovery | Ergonomics Category & Sub-Second SKU Filtering`

### Scene 4: AI Purchasing Consultant Prompt
- **Time Range**: 0:26 – 0:36 (300 frames)
- **Source**: Headless browser render (`http://127.0.0.1:5173/?prompt=Equip+an+ergonomic+workstation+under+500&budget=500`)
- **Key Elements**:
  - Procurement Request input box with active prompt
  - Budget input set to `$500`
  - Provider indicator: `Provider: Gemini (gemini-3.8-flash | Fallback: gemini-3.5-flash-lite)`
- **Caption**: `AI Purchasing Consultant | Natural-Language Intent Grounded in Catalog SKUs`

### Scene 5: Grounded Proposal & Risk Scoring
- **Time Range**: 0:36 – 0:46 (300 frames)
- **Source**: Headless browser render (`http://127.0.0.1:5173/?prompt=Equip+an+ergonomic+workstation+with+chair+under+500&budget=500&auto=true&provider=mock`)
- **Key Elements**:
  - Intent interpretation card
  - Grounded item recommendations with SKU mapping
  - Authoritative subtotal calculation
  - Transparent Transaction Risk Assessment: `LOW RISK (15/100)`
- **Caption**: `Dual-Model Gemini Resilience | Automated Upstream Fallback & Transparent Risk Scoring`

### Scene 6: Cart & PayPal Orders v2 Integration
- **Time Range**: 0:46 – 0:55 (270 frames)
- **Source**: Headless browser render (`http://127.0.0.1:5173/?view=cart`)
- **Key Elements**:
  - Slide-out Cart Drawer
  - Line items with unit prices and quantity controls
  - Official PayPal JavaScript SDK smart buttons container
  - Security note: Server-side price enforcement before capture
- **Caption**: `Cart & Checkout | PayPal Orders v2 REST API & JavaScript SDK Integration`

### Scene 7: Transaction Ledger & PDF Receipt
- **Time Range**: 0:55 – 1:05 (300 frames)
- **Source**: Headless browser render (`http://127.0.0.1:5173/?view=history&order=3d585126-21eb-4898-a79f-3b67d6790877`)
- **Key Elements**:
  - Transaction Ledger modal with 5 historical transactions
  - Expanded view of verified completed Sandbox order `3d585126`
  - PayPal Order ID `6V772492VC732812R` and Capture ID `74868969NJ629324C`
  - "Download Official Receipt (PDF)" action button
- **Caption**: `Audit Trail & Settlement | Historical Order 3d585126 & Official PDF Receipts`

### Scene 8: Security Safeguards & Submission Freeze
- **Time Range**: 1:05 – 1:13 (240 frames)
- **Background**: Deep Fintech Navy (`#102A43`)
- **Key Elements**:
  - 76 Passing Backend Tests (100% Green)
  - Zero Client Secret Leakage Guaranteed
  - Authoritative Database Preserved
  - Ready for Hackathon Review
- **Caption**: `PayPilot AI | Technically Credible, Resilient & Hackathon Ready`

