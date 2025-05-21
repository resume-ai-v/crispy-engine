# ----------------------------------
# ✅ FILE: jobs/form_autofiller.py
# ----------------------------------

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import logging

def autofill_application_form(job_url, resume_text, user_info):
    missing_fields = []
    log = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(job_url, timeout=15000)  # 15s timeout
                log.append(f"🌐 Navigated to {job_url}")
            except PlaywrightTimeoutError:
                log.append("❌ Page load timed out.")
                missing_fields.append("job_url_unreachable")
                return missing_fields

            try:
                page.fill('input[name="fullName"]', user_info.get("name", "John Doe"))
                page.fill('input[name="email"]', user_info.get("email", "john@example.com"))
                page.fill('textarea[name="resume"]', resume_text)
                log.append("✅ Filled basic form fields.")
            except Exception as e:
                log.append(f"⚠️ Error filling basic fields: {e}")
                missing_fields.append("basic_info_fields")

            try:
                page.click('button[type="submit"]')
                log.append("✅ Clicked submit button.")
            except Exception as e:
                log.append(f"⚠️ Submit button not found: {e}")
                missing_fields.append("submit_button")

            browser.close()

    except Exception as outer:
        log.append(f"❌ Critical Playwright error: {outer}")
        missing_fields.append("playwright_error")

    for entry in log:
        print(entry)

    return missing_fields
