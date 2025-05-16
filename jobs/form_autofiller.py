# ----------------------------------
# ✅ FILE: jobs/form_autofiller.py
# ----------------------------------

from playwright.sync_api import sync_playwright

def autofill_application_form(job_url, resume_text, user_info):
    missing_fields = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(job_url)

        try:
            page.fill('input[name="fullName"]', user_info.get("name", "John Doe"))
            page.fill('input[name="email"]', user_info.get("email", "john@example.com"))
            page.fill('textarea[name="resume"]', resume_text)
        except:
            missing_fields.append("basic info fields")

        try:
            page.click('button[type="submit"]')
        except:
            missing_fields.append("submit_button")

        browser.close()

    return missing_fields
