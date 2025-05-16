import os
import json
import requests
import pickle
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

load_dotenv()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_API_URL = "https://jsearch.p.rapidapi.com/search"
CACHE_FILE = "jobs/job_cache.json"
VECTOR_INDEX = "jobs/vector_index.pkl"
MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def get_jobs_from_jsearch(query, location="United States", num_pages=1):
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": f"{query} in {location}",
        "page": "1",
        "num_pages": str(num_pages)
    }

    try:
        response = requests.get(JSEARCH_API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        raw_jobs = response.json().get("data", [])
        jobs = [format_job(job) for job in raw_jobs]
        save_job_cache(jobs)
        index_job_vectors(jobs)
        return jobs
    except Exception as e:
        print("⚠️ API Fetch Failed:", e)
        return load_job_cache()


def format_job(job):
    return {
        "title": job.get("job_title", ""),
        "company": job.get("employer_name", ""),
        "location": job.get("job_city", "Remote"),
        "type": job.get("job_employment_type", "Full Time"),
        "jd_text": job.get("job_description", ""),
        "apply_link": job.get("job_apply_link", "")
    }


def save_job_cache(jobs):
    with open(CACHE_FILE, "w") as f:
        json.dump(jobs, f, indent=2)


def load_job_cache():
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except:
        return []


def index_job_vectors(jobs):
    descriptions = [job["jd_text"] for job in jobs]
    embeddings = MODEL.encode(descriptions, show_progress_bar=False)
    with open(VECTOR_INDEX, "wb") as f:
        pickle.dump(embeddings, f)


def get_similar_jobs(user_resume_text, top_n=5):
    jobs = load_job_cache()
    if not os.path.exists(VECTOR_INDEX):
        return jobs[:top_n]

    with open(VECTOR_INDEX, "rb") as f:
        job_vectors = pickle.load(f)

    resume_vector = MODEL.encode([user_resume_text])[0]
    scores = cosine_similarity([resume_vector], job_vectors)[0]

    sorted_indices = scores.argsort()[::-1][:top_n]
    return [jobs[i] for i in sorted_indices]

