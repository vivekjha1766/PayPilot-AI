import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

FPS = 30
WIDTH = 1920
HEIGHT = 1080

# Color Palette
NAVY = (16, 42, 67)
NAVY_DEEP = (10, 25, 41)
BRAND_BLUE = (0, 112, 224)
WHITE = (255, 255, 255)
SLATE_MUTED = (160, 174, 192)
FOREST = (21, 128, 61)
BORDER_COLOR = (220, 227, 234)

def get_font(size: int, bold: bool = False):
    font_names = [
        "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
    ]
    for fn in font_names:
        if os.path.exists(fn):
            try:
                return ImageFont.truetype(fn, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_caption_banner(img: Image.Image, category_text: str, main_text: str) -> Image.Image:
    """Draws a clean, non-intrusive lower-third banner with editorial typography."""
    img = img.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Banner dimensions
    banner_w = 1100
    banner_h = 74
    banner_x = (WIDTH - banner_w) // 2
    banner_y = HEIGHT - banner_h - 40

    # Draw rounded dark navy background
    draw.rounded_rectangle(
        [banner_x, banner_y, banner_x + banner_w, banner_y + banner_h],
        radius=12,
        fill=(16, 42, 67, 235),
        outline=(0, 112, 224, 255),
        width=2,
    )

    # Accent blue pill on left
    draw.rounded_rectangle(
        [banner_x + 18, banner_y + 16, banner_x + 24, banner_y + banner_h - 16],
        radius=3,
        fill=(0, 112, 224, 255),
    )

    font_cat = get_font(13, bold=True)
    font_main = get_font(18, bold=True)

    draw.text((banner_x + 36, banner_y + 14), category_text.upper(), font=font_cat, fill=(0, 168, 255, 255))
    draw.text((banner_x + 36, banner_y + 36), main_text, font=font_main, fill=(255, 255, 255, 255))

    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def create_title_card() -> Image.Image:
    """Generates the opening high-impact title card."""
    card = Image.new("RGB", (WIDTH, HEIGHT), NAVY_DEEP)
    draw = ImageDraw.Draw(card)

    # Decorative header stripe
    draw.rectangle([0, 0, WIDTH, 6], fill=BRAND_BLUE)

    font_brand = get_font(68, bold=True)
    font_sub = get_font(26, bold=False)
    font_badge = get_font(14, bold=True)

    # Brand Title
    draw.text((120, 280), "PayPilot AI", font=font_brand, fill=WHITE)
    draw.rectangle([120, 370, 240, 376], fill=BRAND_BLUE)

    # Subtitle
    draw.text((120, 400), "Enterprise Purchasing Consultant & PayPal Orders v2 Engine", font=font_sub, fill=WHITE)
    draw.text((120, 445), "Catalog-Grounded Recommendations · Resilient Dual-Model Gemini · Verifiable Audit Ledger", font=get_font(18), fill=SLATE_MUTED)

    # Architectural badge chips
    badges = [
        "FastAPI Backend",
        "React 19 + TypeScript",
        "PayPal Orders v2 REST",
        "Google Gemini 3.8 / 3.5 Fallback",
        "SQLAlchemy 2.x Ledger",
        "Official PDF Receipts",
    ]

    bx = 120
    by = 540
    for badge in badges:
        bw = len(badge) * 10 + 36
        draw.rounded_rectangle([bx, by, bx + bw, by + 40], radius=8, fill=(24, 55, 84), outline=BRAND_BLUE, width=1)
        draw.text((bx + 18, by + 10), badge, font=font_badge, fill=WHITE)
        bx += bw + 18
        if bx > WIDTH - 300:
            bx = 120
            by += 55

    # Footer note
    draw.text((120, 880), "PayPilot AI · Milestone 6 Product Demonstration · Hackathon Final", font=get_font(16), fill=SLATE_MUTED)
    draw.text((WIDTH - 360, 880), "Production Verification Freeze", font=get_font(16, bold=True), fill=(0, 200, 100))

    return card

def create_closing_card() -> Image.Image:
    """Generates the closing conclusion card."""
    card = Image.new("RGB", (WIDTH, HEIGHT), NAVY_DEEP)
    draw = ImageDraw.Draw(card)

    draw.rectangle([0, 0, WIDTH, 6], fill=BRAND_BLUE)

    font_brand = get_font(60, bold=True)
    font_sub = get_font(24, bold=False)
    font_stat = get_font(36, bold=True)
    font_lbl = get_font(14, bold=False)

    draw.text((120, 220), "Ready for Deployment & Evaluation", font=font_brand, fill=WHITE)
    draw.text((120, 305), "PayPilot AI delivers technical credibility, resilient AI, and uncompromised payment safety.", font=font_sub, fill=SLATE_MUTED)

    stats = [
        ("76 / 76", "Backend Tests Passing (100%)"),
        ("0 Errors", "Frontend Production Build"),
        ("Dual-Model", "Gemini 3.8 / 3.5 Resilience"),
        ("100% Intact", "Historical Database Preserved"),
        ("Zero Leakage", "API Keys & Secrets Protected"),
        ("REST v2", "PayPal Orders & Sandbox Capture"),
    ]

    sx = 120
    sy = 420
    for val, label in stats:
        sw = 520
        sh = 95
        draw.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=10, fill=(24, 55, 84), outline=(40, 80, 120), width=1)
        draw.text((sx + 24, sy + 14), val, font=font_stat, fill=(0, 200, 255))
        draw.text((sx + 24, sy + 58), label, font=font_lbl, fill=WHITE)
        sx += sw + 30
        if sx > WIDTH - 400:
            sx = 120
            sy += sh + 25

    draw.text((120, 880), "PayPilot AI · Developed with Google Antigravity IDE", font=get_font(16), fill=SLATE_MUTED)
    return card

def main():
    print("Building PayPilot AI 73-second demonstration video...")

    frames_dir = "demo/frames"
    s1 = Image.open(os.path.join(frames_dir, "scene1_storefront.png")).resize((WIDTH, HEIGHT))
    s2 = Image.open(os.path.join(frames_dir, "scene2_catalog_filter.png")).resize((WIDTH, HEIGHT))
    s3 = Image.open(os.path.join(frames_dir, "scene3_assistant_query.png")).resize((WIDTH, HEIGHT))
    s4 = Image.open(os.path.join(frames_dir, "scene4_assistant_plan.png")).resize((WIDTH, HEIGHT))
    s5 = Image.open(os.path.join(frames_dir, "scene5_cart_drawer.png")).resize((WIDTH, HEIGHT))
    s6 = Image.open(os.path.join(frames_dir, "scene6_transaction_ledger.png")).resize((WIDTH, HEIGHT))

    title_card = create_title_card()
    closing_card = create_closing_card()

    scenes = [
        (title_card, "System Architecture", "PayPilot AI | Enterprise Procurement & PayPal Orders v2 Engine", 9.0),
        (s1, "Authoritative Storefront", "Authoritative Storefront | Real-Time Stock & Certified Unit Pricing", 9.0),
        (s2, "Catalog Discovery", "Catalog Discovery | Ergonomics Category & Sub-Second SKU Filtering", 8.0),
        (s3, "Procurement Intelligence", "AI Purchasing Consultant | Natural-Language Intent Grounded in Catalog SKUs", 10.0),
        (s4, "Resilient Inference", "Dual-Model Gemini Resilience | Automated Upstream Fallback & Transparent Risk Scoring", 10.0),
        (s5, "Payment Integration", "Cart & Checkout | PayPal Orders v2 REST API & JavaScript SDK Integration", 9.0),
        (s6, "Audit Ledger & Settlement", "Audit Trail & Settlement | Historical Order 3d585126 & Official PDF Receipts", 10.0),
        (closing_card, "Production Readiness", "PayPilot AI | Technically Credible, Resilient & Hackathon Ready", 8.0),
    ]

    total_duration = sum(dur for _, _, _, dur in scenes)
    print(f"Total planned scenes: {len(scenes)}, duration: {total_duration:.1f}s")

    # Render scene images with caption overlay
    processed_scenes = []
    for img, cat, cap, dur in scenes:
        overlayed = draw_caption_banner(img, cat, cap)
        processed_scenes.append((np.array(overlayed), dur))

    output_path = "demo/PayPilot_AI_Demo.mp4"
    os.makedirs("demo", exist_ok=True)

    fade_frames = 15  # 0.5s crossfade transition

    writer = imageio.get_writer(
        output_path,
        fps=FPS,
        codec="libx264",
        pixelformat="yuv420p",
        macro_block_size=1,
    )

    total_frames_written = 0

    for idx, (scene_arr, dur) in enumerate(processed_scenes):
        scene_frame_count = int(dur * FPS)
        
        # If there is a next scene, hold for (scene_frame_count - fade_frames) then fade
        if idx < len(processed_scenes) - 1:
            hold_count = scene_frame_count - fade_frames
            next_arr = processed_scenes[idx + 1][0]

            for _ in range(hold_count):
                writer.append_data(scene_arr)
                total_frames_written += 1

            for f in range(fade_frames):
                alpha = (f + 1) / float(fade_frames)
                blended = ((1.0 - alpha) * scene_arr.astype(float) + alpha * next_arr.astype(float)).astype(np.uint8)
                writer.append_data(blended)
                total_frames_written += 1
        else:
            # Final scene holds for full duration
            for _ in range(scene_frame_count):
                writer.append_data(scene_arr)
                total_frames_written += 1

    writer.close()

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"SUCCESS: Generated {output_path}")
    print(f"Total frames: {total_frames_written} ({total_frames_written / FPS:.1f}s at {FPS} FPS)")
    print(f"File size: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    main()

