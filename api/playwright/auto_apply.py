from playwright.sync_api import sync_playwright
import tempfile
import os

def apply_to_job_site(resume, job_url, job_title, company):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(resume.encode("utf-8"))
        resume_path = tmp.name
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(job_url, timeout=60000)
            # EXAMPLE: These selectors need to be customized per job site!
            if page.query_selector('input[type="file"]'):
                page.set_input_files('input[type="file"]', resume_path)
            elif page.query_selector('textarea'):
                page.fill('textarea', resume)
            browser.close()
        os.unlink(resume_path)
        return "Auto-apply simulated (customize selectors for production!)"
    except Exception as e:
        return f"Auto-apply failed: {str(e)}"
