# career_ai_project/jobs/scrape_job.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_job_posting(url: str) -> tuple[str, str, str]:
    """
    Scrapes job description, role, and company name from a given job posting URL.

    Args:
        url (str): Public job post URL

    Returns:
        tuple: (jd_text, role_guess, company_guess)
    """
    if not url or not url.startswith("http"):
        return "", None, None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; CareerAI/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        jd_text = soup.get_text(separator="\n", strip=True)
        jd_text = jd_text[:5000]  # Truncate if too long

        # Guess role based on presence of key terms
        common_roles = ["Data Analyst", "Software Engineer", "AI Engineer", "Product Manager"]
        role_guess = next((role for role in common_roles if role.lower() in jd_text.lower()), "Unknown Role")

        # Guess company from domain
        parsed_url = urlparse(url)
        domain_parts = parsed_url.hostname.split(".")
        company_guess = domain_parts[-2].capitalize() if len(domain_parts) >= 2 else "Unknown Company"

        return jd_text, role_guess, company_guess

    except Exception as e:
        print(f"❌ Scrape Error: {e}")
        return "", None, None
