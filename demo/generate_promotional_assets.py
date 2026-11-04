"""
PayPilot AI — Promotional Asset Generation Pipeline (Part 3)

Generates:
  demo/promotional/paypilot-project-cover.png
  demo/promotional/paypilot-feature-showcase.png
  demo/promotional/paypilot-architecture-showcase.png
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PROMO_DIR = "demo/promotional"
SHOTS_DIR = "demo/screenshots"
os.makedirs(PROMO_DIR, exist_ok=True)

WIDTH = 1920
HEIGHT = 1080

NAVY_DEEP = (10, 25, 41)
NAVY = (16, 42, 67)
BRAND_BLUE = (0, 112, 224)
CYAN_ACCENT = (0, 200, 255)
WHITE = (255, 255, 255)
SLATE_MUTED = (160, 174, 192)
SLATE_BG = (247, 248, 250)
BORDER_GRAY = (220, 227, 234)


def get_font(size: float, bold: bool = False, mono: bool = False):
    size_int = int(round(size))
    if mono:
        candidates = ["C:\\Windows\\Fonts\\consola.ttf", "C:\\Windows\\Fonts\\cour.ttf"]
    else:
        candidates = [
            "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        ]
    for fn in candidates:
        if os.path.exists(fn):
            try:
                return ImageFont.truetype(fn, size_int)
            except Exception:
                continue
    return ImageFont.load_default()


def create_project_cover():
    print("  Creating paypilot-project-cover.png...")
    img = Image.new("RGB", (WIDTH, HEIGHT), NAVY_DEEP)
    draw = ImageDraw.Draw(img)

    # Subtle ambient gradient / grid
    for y in range(0, HEIGHT, 40):
        draw.line([0, y, WIDTH, y], fill=(16, 32, 50), width=1)
    for x in range(0, WIDTH, 40):
        draw.line([x, 0, x, HEIGHT], fill=(16, 32, 50), width=1)

    # Outer decorative frame
    draw.rectangle([30, 30, WIDTH - 30, HEIGHT - 30], outline=BRAND_BLUE, width=2)
    draw.rectangle([36, 36, WIDTH - 36, HEIGHT - 36], outline=(0, 112, 224), width=1)

    # Brand Pill
    draw.rounded_rectangle([90, 80, 210, 118], radius=6, fill=BRAND_BLUE)
    draw.text((112, 88), "PAYPILOT", font=get_font(15, bold=True), fill=WHITE)

    # Title & Tagline
    draw.text((90, 140), "PayPilot AI", font=get_font(56, bold=True), fill=WHITE)
    draw.text((90, 215), "Shop smarter. Decide better. Pay securely.", font=get_font(26, bold=True), fill=CYAN_ACCENT)
    draw.text((90, 260), "AI-Powered Procurement · Grounded Recommendations · PayPal Orders v2 Settlement", font=get_font(17), fill=SLATE_MUTED)

    # Central Visual: Framed Desktop Screenshot
    hero_shot = Image.open(os.path.join(SHOTS_DIR, "01-homepage-hero.png"))
    # Resize screenshot with 16:9 ratio to fit beautifully in the lower-right / center
    shot_w = 1160
    shot_h = 652
    hero_resized = hero_shot.resize((shot_w, shot_h), Image.Resampling.LANCZOS)

    shot_x = WIDTH - shot_w - 90
    shot_y = 330

    # Draw shadow
    draw.rounded_rectangle([shot_x - 6, shot_y - 6, shot_x + shot_w + 6, shot_y + shot_h + 6], radius=10, fill=(0, 0, 0))
    # Border
    draw.rounded_rectangle([shot_x - 3, shot_y - 3, shot_x + shot_w + 3, shot_y + shot_h + 3], radius=8, outline=BRAND_BLUE, width=2)
    img.paste(hero_resized, (shot_x, shot_y))

    # Left Feature Highlights
    highlights = [
        ("Grounded Gemini AI", "Direct warehouse catalog inventory grounding with primary and fallback model resilience."),
        ("PayPal Orders v2", "Server-authoritative order creation, client idempotency keys, and automated capture reconciliation."),
        ("Payment Integrity", "Atomic SQLite inventory movement ledger preventing duplicate charges or negative stock."),
        ("Auditable Invoicing", "Authoritative transaction ledger with server-compiled ReportLab PDF receipts."),
    ]

    hy = 340
    for title, desc in highlights:
        draw.rounded_rectangle([90, hy, shot_x - 40, hy + 130], radius=8, fill=NAVY, outline=(0, 112, 224), width=1)
        draw.rounded_rectangle([108, hy + 20, 114, hy + 46], radius=2, fill=CYAN_ACCENT)
        draw.text((126, hy + 18), title, font=get_font(18, bold=True), fill=WHITE)

        words = desc.split(" ")
        lines = []
        cur = []
        for w in words:
            if len(" ".join(cur + [w])) > 44:
                lines.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(" ".join(cur))

        for l_idx, l in enumerate(lines):
            draw.text((126, hy + 50 + l_idx * 22), l, font=get_font(13), fill=SLATE_MUTED)

        hy += 150

    # Bottom Footer
    draw.text((90, HEIGHT - 70), "Official Hackathon Submission · Production Verified · Real Interactive Implementation", font=get_font(14), fill=SLATE_MUTED)
    draw.text((WIDTH - 380, HEIGHT - 70), "Milestone 6 Freeze Complete", font=get_font(14, bold=True), fill=(0, 220, 120))

    img.save(os.path.join(PROMO_DIR, "paypilot-project-cover.png"))
    print("  -> Saved paypilot-project-cover.png")


def create_feature_showcase():
    print("  Creating paypilot-feature-showcase.png...")
    img = Image.new("RGB", (WIDTH, HEIGHT), NAVY_DEEP)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((80, 50), "PAYPILOT AI FEATURE SHOWCASE", font=get_font(14, bold=True), fill=CYAN_ACCENT)
    draw.text((80, 75), "From Natural-Language Prompt to PayPal Settlement", font=get_font(36, bold=True), fill=WHITE)
    draw.text((80, 125), "An integrated, enterprise-grade procurement workflow built on verifiable architectures.", font=get_font(16), fill=SLATE_MUTED)

    # 3-Panel Feature Showcase:
    # Panel 1: Catalog & Search (02-product-catalogue.png)
    # Panel 2: Grounded AI Assistant (04-ai-purchasing-assistant.png)
    # Panel 3: PayPal Checkout & Ledger (06-cart-checkout.png)

    cards = [
        ("01. CATALOG DISCOVERY", "Authoritative Server-Side Pricing", "02-product-catalogue.png", 80),
        ("02. GROUNDED AI CONSULTANT", "Explainable Multi-Factor Risk Scoring", "04-ai-purchasing-assistant.png", 670),
        ("03. PAYPAL V2 SETTLEMENT", "Idempotent Orders & Capture Reconciliation", "06-cart-checkout.png", 1260),
    ]

    panel_w = 560
    panel_h = 760

    for step, title, img_name, px in cards:
        # Card Background Frame
        draw.rounded_rectangle([px, 180, px + panel_w, 180 + panel_h], radius=10, fill=NAVY, outline=BRAND_BLUE, width=1)

        # Header inside panel
        draw.text((px + 24, 204), step, font=get_font(12, bold=True), fill=CYAN_ACCENT)
        draw.text((px + 24, 226), title, font=get_font(18, bold=True), fill=WHITE)

        # Embedded actual screenshot
        shot_path = os.path.join(SHOTS_DIR, img_name)
        if os.path.exists(shot_path):
            raw_shot = Image.open(shot_path)
            # Crop/fit into panel
            shot_inset_w = panel_w - 40
            shot_inset_h = panel_h - 130
            # Crop to aspect
            aspect = shot_inset_w / shot_inset_h
            orig_w, orig_h = raw_shot.size
            crop_h = int(orig_w / aspect)
            cropped = raw_shot.crop((0, 0, orig_w, min(orig_h, crop_h)))
            resized = cropped.resize((shot_inset_w, shot_inset_h), Image.Resampling.LANCZOS)

            draw.rounded_rectangle([px + 18, 278, px + 22 + shot_inset_w, 282 + shot_inset_h], radius=6, fill=(0, 0, 0))
            img.paste(resized, (px + 20, 280))

    # Bottom footer
    draw.text((80, HEIGHT - 55), "PayPilot AI · Built with FastAPI, React, TypeScript, Gemini 3.8/3.5, and PayPal Orders v2", font=get_font(13), fill=SLATE_MUTED)
    draw.text((WIDTH - 360, HEIGHT - 55), "100% Genuine Application Captures", font=get_font(13, bold=True), fill=(0, 220, 120))

    img.save(os.path.join(PROMO_DIR, "paypilot-feature-showcase.png"))
    print("  -> Saved paypilot-feature-showcase.png")


def create_architecture_showcase():
    print("  Creating paypilot-architecture-showcase.png...")
    img = Image.new("RGB", (WIDTH, HEIGHT), NAVY_DEEP)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((80, 50), "PAYPILOT AI TECHNICAL ARCHITECTURE", font=get_font(14, bold=True), fill=CYAN_ACCENT)
    draw.text((80, 75), "Decoupled Advisory AI & Authoritative Payment Integrity Engine", font=get_font(34, bold=True), fill=WHITE)
    draw.text((80, 125), "Strict separation between natural-language advisory models and server-authoritative settlement validation.", font=get_font(16), fill=SLATE_MUTED)

    # Architecture Columns (4 Pillars)
    layers = [
        ("CLIENT LAYER", "React 18 · TypeScript · Vite", [
            ("Storefront UI", "Tailwind CSS styling with PayPal enterprise design system."),
            ("PayPal JS SDK", "Containerized PayPal Sandbox Smart Buttons."),
            ("Idempotency Gen", "Client UUID checkout keys preventing duplicate submissions."),
            ("State Management", "Live cart recalculation with optimistic validation."),
        ], 80),
        ("FASTAPI GATEWAY", "Python 3.13 · Pydantic v2", [
            ("Router Modules", "Clean separation: catalog, assistant, orders, payments."),
            ("Input Validation", "Strict Pydantic schemas validating budgets & SKUs."),
            ("Security Hardening", "CORS policy, sanitized error messages, secret shielding."),
            ("Asynchronous I/O", "High-throughput async endpoints with bounded timeouts."),
        ], 505),
        ("AI RESILIENCE LAYER", "Google GenAI SDK · Failover", [
            ("Primary Model", "gemini-3.8-flash with structured JSON response schema."),
            ("Fallback Model", "gemini-3.5-flash-lite on 503 high-demand or 429 limits."),
            ("Deterministic Mock", "Deterministic rule engine for test mode & zero-rate limits."),
            ("Advisory Boundary", "AI suggestions never modify inventory or payment state."),
        ], 930),
        ("PAYMENT INTEGRITY", "PayPal Orders v2 · SQLite", [
            ("Atomic Ledger", "SQLite inventory ledger with automatic rollback on race conditions."),
            ("Reconciliation", "Automated PayPal REST poll if client network drops."),
            ("Snapshot Integrity", "Historical orders locked with immutable prices."),
            ("Official Receipts", "Server-compiled ReportLab PDF receipts with verification seals."),
        ], 1355),
    ]

    col_w = 385
    col_h = 750

    for l_title, l_tech, items, cx in layers:
        # Layer Card Frame
        draw.rounded_rectangle([cx, 180, cx + col_w, 180 + col_h], radius=10, fill=NAVY, outline=BRAND_BLUE, width=1)

        # Header
        draw.text((cx + 20, 205), l_title, font=get_font(14, bold=True), fill=CYAN_ACCENT)
        draw.text((cx + 20, 230), l_tech, font=get_font(12), fill=SLATE_MUTED)
        draw.line([cx + 20, 255, cx + col_w - 20, 255], fill=(0, 112, 224), width=1)

        # Items
        iy = 275
        for item_title, item_desc in items:
            draw.rounded_rectangle([cx + 16, iy, cx + col_w - 16, iy + 105], radius=6, fill=(20, 36, 56), outline=(0, 112, 224, 80), width=1)
            draw.text((cx + 28, iy + 12), item_title, font=get_font(15, bold=True), fill=WHITE)

            words = item_desc.split(" ")
            lines = []
            cur = []
            for w in words:
                if len(" ".join(cur + [w])) > 32:
                    lines.append(" ".join(cur))
                    cur = [w]
                else:
                    cur.append(w)
            if cur:
                lines.append(" ".join(cur))

            for l_idx, l in enumerate(lines):
                draw.text((cx + 28, iy + 38 + l_idx * 20), l, font=get_font(12), fill=SLATE_MUTED)

            iy += 118

    # Bottom footer
    draw.text((80, HEIGHT - 55), "PayPilot AI Architecture Specification · Zero Deprecated APIs · Production Ready", font=get_font(13), fill=SLATE_MUTED)
    draw.text((WIDTH - 360, HEIGHT - 55), "SQLAlchemy 2.x & SQLite Verified", font=get_font(13, bold=True), fill=(0, 220, 120))

    img.save(os.path.join(PROMO_DIR, "paypilot-architecture-showcase.png"))
    print("  -> Saved paypilot-architecture-showcase.png")


def main():
    print("--- [Part 3] Generating Professional Promotional Assets ---")
    create_project_cover()
    create_feature_showcase()
    create_architecture_showcase()
    print("ALL 3 PROMOTIONAL ASSETS GENERATED 100% SUCCESSFULLY!\n")


if __name__ == "__main__":
    main()

