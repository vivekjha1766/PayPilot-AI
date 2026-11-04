# PayPilot AI — Automated Demo Narration Script

**Project**: PayPilot AI: Enterprise Purchasing Consultant & PayPal Orders v2 Engine  
**Target Video**: `demo/PayPilot_AI_Automated_Demo.mp4`  
**Duration**: 82.0 Seconds (1920 × 1080 Full HD, 30 FPS, H.264 / AAC)  
**Tone**: Authoritative, concise, executive fintech presentation  

---

## Narration & Interaction Timeline

| Timecode | Scene Title | Browser Automation Actions | Voiceover Narration |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:08** | **1. Brand Introduction** | Open `http://127.0.0.1:5173/`. Wait for network idle. Highlight PayPilot wordmark, tagline, and `API Online` live backend indicator. | *"Meet PayPilot AI — a smarter way to make purchasing decisions."* |
| **0:08 – 0:20** | **2. Product Storefront** | Smooth scroll to Authoritative Merchant Catalog. Click `Furniture` category filter. Search for `"AeroPro"`. Highlight AeroPro Ergonomic Office Chair ($289.50, stock 44, SKU `CHAIR-ERGO-01`). Clear search, return to `ALL`. | *"Explore products through a clean, intuitive storefront with real catalogue pricing and inventory availability."* |
| **0:20 – 0:37** | **3. AI Purchasing Assistant** | Smooth scroll up to Purchasing Consultant. Click prompt input. Type: `"I need an ergonomic chair for back support under $350."` Type budget: `"350"`. Click `Consult`. Wait for real backend inference. Highlight grounded proposal. | *"Need help choosing? Simply describe what you're looking for. Our AI purchasing consultant analyses your requirements and recommends products grounded in the actual catalogue."* |
| **0:37 – 0:48** | **4. Gemini Resilience** | Hover over provider badge (`Provider: Gemini`). Highlight resilience fallback notification and explainable Transaction Risk Assessment card (`LOW RISK (15/100)`). | *"With resilient Gemini integration and a deterministic test mode, recommendations remain transparent and dependable."* |
| **0:48 – 0:60** | **5. Cart & Checkout** | Click `+ Add to Order` / recommendation action. Cart drawer slides open. Display certified line items, quantity calculations, and official `@paypal/react-paypal-js` PayPal smart buttons. (Do not trigger payment). Close drawer. | *"Once you're ready, review your cart and proceed to secure PayPal-powered checkout."* |
| **0:60 – 0:76** | **6. Transaction Ledger & Receipt** | Click `History` in top navbar. Transaction Ledger opens showing 5 historical transactions. Click completed order `3d585126...` to expand audit trail, PayPal IDs (`6V772492VC732812R`), and click `Download Official Receipt (PDF)`. | *"Every completed transaction is traceable through an auditable transaction history, with downloadable official PDF receipts."* |
| **0:76 – 0:82** | **7. Closing Branded Tagline** | Close modal. Display high-impact branded closing frame with architecture badges and tagline. | *"PayPilot AI. Shop smarter. Decide better. Pay securely."* |

---

## Technical Voice Specifications
- **Speech Engine**: Windows Speech Synthesis (`System.Speech.Synthesis`)
- **Voice**: Natural English Narration
- **Sampling Rate**: 44.1 kHz, 16-bit Stereo PCM / AAC
- **Audio Mixing**: Voiceover balanced with subtle ambient background audio (ducked -18 dB under voice)

