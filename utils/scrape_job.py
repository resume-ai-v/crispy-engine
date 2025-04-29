import requests
from bs4 import BeautifulSoup


def scrape_job_posting(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        jd_text = soup.get_text(separator="\n", strip=True)

        # Example placeholder (real logic can improve later)
        role = "Data Analyst" if "Data Analyst" in jd_text else "Job Role"
        company = "Company Name"

        return jd_text[:5000], role, company
    except Exception as e:
        print(f"Scrape Error: {e}")
        return "", None, None
