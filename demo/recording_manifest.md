# PayPilot AI — Production Recording Manifest (Demo 2.0)

**Generated**: November 4, 2026  
**Environment**: Windows 11 · Python 3.13.9 · Microsoft Edge (Playwright) · FFmpeg  
**Target Video**: `demo/PayPilot_AI_Final_Demo.mp4`  
**Subtitle Deliverable**: `demo/PayPilot_AI_Final_Demo.srt`  

---

## 1. Master Media Specifications

| Parameter | Specification | Verified Output | Status |
| :--- | :--- | :--- | :--- |
| **Duration** | 100.0s – 120.0s | **`112.0 seconds`** (`00:01:52.00`) | **PASS** |
| **Resolution** | 1920 × 1080 (16:9 Full HD) | **`1920 × 1080`** | **PASS** |
| **Frame Rate** | 30.0 FPS | **`30.0 FPS`** (`3,360 frames`) | **PASS** |
| **Video Codec** | H.264 (`yuv420p` progressive) | **`h264 (High) (avc1)`** @ 250 kb/s | **PASS** |
| **Audio Stream** | AAC (Stereo/Mono, 44.1 kHz) | **`aac (LC) (mp4a)`** @ 177 kb/s, 44.1 kHz | **PASS** |
| **File Size** | Optimized streaming MP4 | **`6.08 MB`** (`6,375,190 bytes`) | **PASS** |
| **Subtitles** | Burned-in + External `.srt` | **Burned into MP4 + `PayPilot_AI_Final_Demo.srt`** | **PASS** |
| **Cursor Overlay** | Visible contrast cursor + click ripple | **Injected `#paypilot-demo-cursor` + `.demo-click-ripple`** | **PASS** |

---

## 2. Deliverable Manifest

The following official files have been compiled into the `demo/` directory:

1. **`demo/PayPilot_AI_Final_Demo.mp4`** (Master 1080p 30 FPS Demonstration Video, 6.08 MB)
2. **`demo/PayPilot_AI_Final_Demo.srt`** (Synchronized English Subtitle Stream, 13 cues)
3. **`demo/PayPilot_AI_Final_Demo_Script.md`** (Complete Narration, Timeline, and Cues)
4. **`demo/PayPilot_AI_Final_Demo_Storyboard.md`** (Visual & Technical Layout Framing)
5. **`demo/record_interactive_demo.py`** (End-to-End Automated Production Script)
6. **`demo/recording_manifest.md`** (This Production & Verification Audit)
7. **`demo/downloaded_receipt_3d585126.pdf`** (Genuinely downloaded official PDF invoice, 2,925 bytes)
8. **`demo/sample_frames/`** (Keyframe verification captures):
   - `scene1_hero.png` (2.0s: Architecture & dual-model banner)
   - `scene2_catalog.png` (15.0s: Search typing, live filter, stock hover)
   - `scene3_assistant.png` (35.0s: Grounded intent proposal & risk score)
   - `scene4_ide_ai.png` (52.0s: IDE code view of Gemini resilience layer)
   - `scene5_cart_paypal.png` (70.0s: Purchase order math & PayPal Smart Buttons)
   - `scene6_ledger_receipt.png` (85.0s: Expanded audit order & PDF download)
   - `scene7_ide_payment.png` (100.0s: IDE code view of payment reconciliation)
   - `scene8_closing.png` (110.0s: Final branded mission & pillar badges)

---

## 3. Real Interactive Elements Demonstrated

Unlike a slideshow or static video, Demo 2.0 captures genuine, dynamic interactions:

- **Visible Mouse Tracking**: Contrasting navy/blue pointer with cyan target dot moves smoothly between UI elements across the screen (`page.mouse.move` with 20–30 intermediate steps).
- **Animated Click Ripples**: Every button click, input selection, and drawer toggle triggers a visible expanding circular ripple (`.demo-click-ripple`).
- **Live Text Input**: Characters are typed sequentially with realistic delay into both the catalog search bar (`"ergonomic chair"`) and the AI consultant prompt (`"I need an ergonomic chair for back support under $350."`).
- **Dynamic State Changes**:
  * Catalog responds in real time to search queries, isolating `AeroPro Ergonomic Chair`.
  * Clicking "Add to Order" immediately increments the navigation bar cart counter and total amount.
  * Opening the `Purchase Order` drawer and clicking `+` and `-` triggers real-time price and tax recalculation ($289.50 ↔ $579.00).
  * Opening the `Transaction Ledger` expands historical order `3d585126...` to display its PayPal Order ID and Capture ID.
- **Genuine File Download**: Clicking `Download Official Receipt (PDF)` triggers an authentic browser download via Playwright's `expect_download` event, capturing the real 2,925-byte PDF compiled by ReportLab on the backend.
- **Transparent Code Architecture**: Scenes 4 and 7 feature high-definition syntax-colored IDE views inspecting the actual repository code (`gemini_provider.py` and `paypal_service.py`), proving real engineering behind the user interface.

---

## 4. Preservation & Safety Audit

The production pipeline enforces non-destructive safeguards:

| Invariant | Target Requirement | Verified Result | Compliance |
| :--- | :--- | :--- | :--- |
| **Database File** | `backend/paypilot.db` untouched | Verified untouched | **100% PASS** |
| **Historical Orders** | Exactly 5 orders | Verified count: **`5`** | **100% PASS** |
| **Sandbox Order** | `3d585126...` preserved intact | `COMPLETED` ($289.50) preserved | **100% PASS** |
| **PayPal Order ID** | `6V772492VC732812R` intact | Unmodified in DB | **100% PASS** |
| **PayPal Capture ID** | `74868969NJ629324C` intact | Unmodified in DB | **100% PASS** |
| **Chair Inventory** | `CHAIR-ERGO-01` stock = 44 | Verified stock: **`44`** | **100% PASS** |
| **New Payments** | ZERO new payments created | Zero PayPal orders/captures created | **100% PASS** |
| **Credentials Safety** | No API keys or tokens in video/logs | Verified zero exposed secrets | **100% PASS** |
| **Backend Test Suite** | All tests passing | **76 / 76 passed (100%)** | **100% PASS** |
| **Frontend Lint & Build** | Clean build with zero errors | **Zero lint errors, clean 5s build** | **100% PASS** |
