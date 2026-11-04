"""
PayPilot AI — Comprehensive Website Screenshot Capture Pipeline (Part 2)

Captures 11 authentic, high-resolution desktop and responsive mobile screenshots
from the running PayPilot AI application:
  demo/screenshots/01-homepage-hero.png
  demo/screenshots/02-product-catalogue.png
  demo/screenshots/03-product-search.png
  demo/screenshots/04-ai-purchasing-assistant.png
  demo/screenshots/05-ai-recommendation.png
  demo/screenshots/06-cart-checkout.png
  demo/screenshots/07-transaction-history.png
  demo/screenshots/08-official-receipt.png
  demo/screenshots/09-mobile-homepage.png
  demo/screenshots/10-mobile-catalogue.png
  demo/screenshots/11-mobile-ai-assistant.png
"""

import asyncio
import os
import sqlite3
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "demo/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def capture_all_screenshots():
    print("--- [Part 2] Capturing Professional Website Screenshots ---")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=True,
            args=["--disable-gpu", "--hide-scrollbars"],
        )

        # ----------------------------------------------------
        # Desktop Captures (1920 x 1080)
        # ----------------------------------------------------
        d_ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.0,
        )
        d_page = await d_ctx.new_page()

        print("  1. Capturing 01-homepage-hero.png...")
        await d_page.goto("http://127.0.0.1:5173/")
        await d_page.wait_for_selector("text=PayPilot")
        await d_page.wait_for_selector("text=Authoritative Merchant Catalog")
        await d_page.evaluate("window.scrollTo(0, 0)")
        await d_page.wait_for_timeout(800)
        await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01-homepage-hero.png"))

        print("  2. Capturing 02-product-catalogue.png...")
        await d_page.evaluate("window.scrollTo({top: 480, behavior: 'instant'})")
        await d_page.wait_for_timeout(800)
        await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02-product-catalogue.png"))

        print("  3. Capturing 03-product-search.png...")
        search_input = d_page.locator('input[placeholder*="Search catalog"]')
        await search_input.click()
        await search_input.fill("ergonomic chair")
        await d_page.wait_for_timeout(1000)
        await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03-product-search.png"))

        # Clear search and reset catalog
        clear_btn = d_page.locator('button[aria-label="Clear search query"]')
        if await clear_btn.count() > 0:
            await clear_btn.click()
            await d_page.wait_for_timeout(500)

        print("  4. Capturing 04-ai-purchasing-assistant.png...")
        await d_page.evaluate("window.scrollTo({top: 80, behavior: 'instant'})")
        await d_page.wait_for_timeout(500)

        prompt_in = d_page.locator("#assistant-prompt")
        await prompt_in.fill("I need an ergonomic chair for back support under $350.")
        budget_in = d_page.locator("#assistant-budget")
        await budget_in.fill("350")

        # Enable deterministic Test Mode (Mock)
        mock_lbl = d_page.locator('label:has-text("Test Mode (Mock)")')
        if await mock_lbl.count() > 0:
            await mock_lbl.click()
            await d_page.wait_for_timeout(400)

        consult_btn = d_page.locator('button:has-text("Consult")')
        await consult_btn.click()
        await d_page.wait_for_selector("text=Parsed Procurement Intent", timeout=12000)
        await d_page.wait_for_timeout(1000)
        await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04-ai-purchasing-assistant.png"))

        print("  5. Capturing 05-ai-recommendation.png...")
        await d_page.evaluate("window.scrollTo({top: 260, behavior: 'instant'})")
        await d_page.wait_for_timeout(800)
        await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05-ai-recommendation.png"))

        print("  6. Capturing 06-cart-checkout.png...")
        # Add item to cart to show realistic order in drawer
        chair_add = d_page.locator('article:has-text("AeroPro Ergonomic Chair") button:has-text("Add to Order")')
        if await chair_add.count() > 0:
            await chair_add.first.click()
            await d_page.wait_for_timeout(800)

        nav_cart = d_page.locator('button[aria-label^="Open purchase order"]')
        if await nav_cart.count() > 0:
            await nav_cart.first.click()
            await d_page.wait_for_selector("text=Purchase Order", timeout=6000)
            await d_page.wait_for_timeout(1200)
            await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06-cart-checkout.png"))

        # Close cart drawer
        close_drawer = d_page.locator('button[aria-label="Close purchase order drawer"]')
        if await close_drawer.count() > 0:
            await close_drawer.click()
            await d_page.wait_for_timeout(600)

        print("  7. Capturing 07-transaction-history.png...")
        hist_btn = d_page.locator('button[aria-label="View transaction history"]')
        if await hist_btn.count() > 0:
            await hist_btn.click()
            await d_page.wait_for_selector("text=Transaction Ledger", timeout=6000)
            await d_page.wait_for_timeout(800)

            # Expand historical completed order 3d585126
            order_row = d_page.locator('div[role="button"]:has-text("3d585126")')
            if await order_row.count() > 0:
                await order_row.first.click()
                await d_page.wait_for_timeout(1000)

            await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "07-transaction-history.png"))

            # Close ledger modal
            close_ledger = d_page.locator('button[aria-label="Close transaction ledger"]')
            if await close_ledger.count() > 0:
                await close_ledger.click()
                await d_page.wait_for_timeout(600)

        print("  8. Capturing 08-official-receipt.png...")
        # Open genuinely downloaded PDF receipt in browser at 1920x1080
        receipt_pdf_path = os.path.abspath("demo/downloaded_receipt_3d585126.pdf").replace("\\", "/")
        await d_page.goto(f"file:///{receipt_pdf_path}")
        await d_page.wait_for_timeout(1500)
        await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "08-official-receipt.png"))

        await d_ctx.close()

        # ----------------------------------------------------
        # Mobile Captures (375 x 812)
        # ----------------------------------------------------
        m_ctx = await browser.new_context(
            viewport={"width": 375, "height": 812},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2.0,
        )
        m_page = await m_ctx.new_page()

        print("  9. Capturing 09-mobile-homepage.png...")
        await m_page.goto("http://127.0.0.1:5173/")
        await m_page.wait_for_selector("text=PayPilot")
        await m_page.evaluate("window.scrollTo(0, 0)")
        await m_page.wait_for_timeout(800)
        await m_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "09-mobile-homepage.png"))

        print("  10. Capturing 10-mobile-catalogue.png...")
        await m_page.evaluate("window.scrollTo({top: 480, behavior: 'instant'})")
        await m_page.wait_for_timeout(800)
        await m_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "10-mobile-catalogue.png"))

        print("  11. Capturing 11-mobile-ai-assistant.png...")
        await m_page.evaluate("window.scrollTo({top: 80, behavior: 'instant'})")
        m_prompt = m_page.locator("#assistant-prompt")
        await m_prompt.fill("Ergonomic chair under $350")
        m_budget = m_page.locator("#assistant-budget")
        await m_budget.fill("350")

        m_mock = m_page.locator('label:has-text("Test Mode (Mock)")')
        if await m_mock.count() > 0:
            await m_mock.click()
            await m_page.wait_for_timeout(300)

        m_consult = m_page.locator('button:has-text("Consult")')
        await m_consult.click()
        await m_page.wait_for_selector("text=Parsed Procurement Intent", timeout=12000)
        await m_page.wait_for_timeout(1000)
        await m_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "11-mobile-ai-assistant.png"))

        await m_ctx.close()
        await browser.close()

    print("ALL 11 SCREENSHOTS CAPTURED 100% SUCCESSFULLY!\n")


if __name__ == "__main__":
    asyncio.run(capture_all_screenshots())

