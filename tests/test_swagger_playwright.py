"""
Playwright automated test script for Swagger UI testing of /api/search.
"""

import asyncio
import os
from playwright.async_api import async_playwright


async def _async_test_swagger_ui_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 1400})
        page = await context.new_page()

        print("1. Navigating to http://127.0.0.1:8000/docs...")
        await page.goto("http://127.0.0.1:8000/docs", wait_until="networkidle")

        opblock = page.locator("#operations-Search-search_products_api_search_get")
        print("2. Expanding GET /api/search...")
        await opblock.locator(".opblock-summary").click()
        await page.wait_for_timeout(500)

        print("3. Clicking 'Try it out'...")
        await opblock.locator("button.try-out__btn").click()
        await page.wait_for_timeout(500)

        # Fill query input
        inputs = await opblock.locator("input").all()
        print(f"4. Found {len(inputs)} parameter inputs.")
        await inputs[0].fill("shoes")
        print("5. Typed 'shoes' into query parameter.")

        print("6. Clicking 'Execute'...")
        await opblock.locator("button.execute").click()
        await page.wait_for_timeout(2000)

        # Verify Response Code
        status_col = opblock.locator(".response .response-col_status").first
        status_code = await status_col.text_content()
        clean_status = status_code.strip()
        print(f"7. Swagger UI Returned Status: {clean_status}")
        assert clean_status == "200", f"Expected 200, got {clean_status}"

        # Verify Response JSON
        body_elem = opblock.locator(".response .microlight, .response .highlight-code").first
        body_text = await body_elem.text_content()
        print(f"8. Response JSON snippet: {body_text[:180]}...")
        assert "Air Stride Lightweight Running Shoes" in body_text

        # Test Case 2: Empty fields execution (simulate user clicking Execute with all fields blank)
        print("\n--- Testing Empty Parameters in Swagger UI ---")
        await inputs[0].fill("")
        print("9. Cleared query field.")
        await opblock.locator("button.execute").click()
        await page.wait_for_timeout(2000)

        status_code_empty = (await opblock.locator(".response .response-col_status").first.text_content()).strip()
        print(f"10. Empty parameters status: {status_code_empty}")
        assert status_code_empty == "200", f"Expected 200, got {status_code_empty}"

        body_text_empty = await opblock.locator(".response .microlight, .response .highlight-code").first.text_content()
        print(f"11. Empty parameters returned {body_text_empty[:120]}...")

        # Save screenshot
        screenshot_path = os.path.join(os.path.dirname(__file__), "swagger_search_verified.png")
        await page.screenshot(path=screenshot_path)
        print(f"12. Verification screenshot saved to: {screenshot_path}")

        await browser.close()
        print("\nAll Swagger UI Playwright tests PASSED successfully!")


def test_swagger_ui_search():
    """Pytest entrypoint executing the Playwright browser test."""
    asyncio.run(_async_test_swagger_ui_search())


if __name__ == "__main__":
    test_swagger_ui_search()

