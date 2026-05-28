import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Auth
load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
}

# Config
OUTPUT_DIR = "raw_data"
RESULTS_PER_PAGE = 100
MAX_PAGES = 10 # 10 * 100 = 1000 results per query (GitHub hard cap)

# Star range buckets to set up stratified sampling later
STAR_BUCKETS = [
    ("500..2000",   "500-2k"),
    ("2001..10000", "2k-10k"),
    ("10001..50000","10k-50k"),
    ("50001..*",    "50k+"),
]

# Search query definitions
LLM_TOPICS = [
    "llm",
    "large-language-model",
    "ai",
    "agent"
    "ai-agent",
    "autonomous-agent",
    "rag",
    "langchain",
]

LEGACY_TOPICS = [
    "machine-learning",
    "ml"
    "deep-learning",
    "neural-network",
]

# Hardcoded legacy ML seed repos to guarantee the canonical libraries are included regardless of how they tag themselves on GitHub
LEGACY_SEED_REPOS = [
    ("pytorch", "pytorch"),
    ("tensorflow", "tensorflow"),
    ("scikit-learn", "scikit-learn"),
    ("keras-team", "keras"),
    ("dmlc", "xgboost"),
    ("microsoft", "LightGBM"),
    ("apache", "mxnet"),
    ("BVLC", "caffe"),
    ("Theano", "Theano"),
]


# Core request helper
def github_get(url: str, params: dict = None) -> dict:
    """Single GET with rate-limit awareness. Sleeps and retries on 403/429."""
    for attempt in range(3):
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code in (403, 429):
            reset_ts = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_for = max(reset_ts - int(time.time()), 1)
            print(f"  Rate limited. Sleeping {sleep_for}s...")
            time.sleep(sleep_for)
        else:
            print(f"  HTTP {response.status_code} on {url}")
            break
    return {}


# Search API
def search_repos(query: str) -> list[dict]:
    """
    Paginate through GitHub Search API for a given query string.
    Returns a flat list of repo objects.
    """
    repos = []
    for page in range(1, MAX_PAGES + 1):
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": RESULTS_PER_PAGE,
            "page": page,
        }
        data = github_get("https://api.github.com/search/repositories", params)
        items = data.get("items", [])
        if not items:
            break
        repos.extend(items)
        print(f"    page {page}: got {len(items)} repos (total so far: {len(repos)})")
        time.sleep(2)  # Search API: stay under 30 req/min authenticated
    return repos


def fetch_cohort_via_search(topics: list[str], extra_filters: str) -> list[dict]:
    """
    Run one search query per topic + star bucket combination.
    Deduplicates by repo ID across all queries.
    Returns list of raw repo dicts from the GitHub API.
    """
    seen_ids = set()
    all_repos = []

    for topic in topics:
        for star_range, label in STAR_BUCKETS:
            query = f"topic:{topic} stars:{star_range} language:Python {extra_filters} fork:false"
            print(f"  Querying: {query}")
            results = search_repos(query)
            for repo in results:
                if repo["id"] not in seen_ids:
                    seen_ids.add(repo["id"])
                    all_repos.append(repo)
            print(f"  → {len(results)} results, {len(all_repos)} unique so far\n")

    return all_repos


# Seed repo fetcher
def fetch_seed_repos(seed_list: list[tuple]) -> list[dict]:
    """Fetch repo metadata for hardcoded owner/repo pairs."""
    repos = []
    for owner, repo in seed_list:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        data = github_get(url)
        if data.get("id"):
            repos.append(data)
            print(f"  Fetched seed repo: {owner}/{repo}")
        time.sleep(0.5)
    return repos


# Save
def save(data: list[dict], filename: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\nSaved {len(data)} repos to {path}")


# Main
if __name__ == "__main__":
    print("=== Fetching LLM / Agentic AI cohort ===")
    llm_repos = fetch_cohort_via_search(
        topics=LLM_TOPICS,
        extra_filters="created:>2022-11-01 stars:>500"
    )
    save(llm_repos, "llm_candidates.json")

    print("\n=== Fetching Legacy ML cohort (search) ===")
    legacy_repos = fetch_cohort_via_search(
        topics=LEGACY_TOPICS,
        extra_filters="created:<2020-01-01 stars:>500"
    )

    print("\n=== Fetching Legacy ML seed repos ===")
    seed_repos = fetch_seed_repos(LEGACY_SEED_REPOS)

    # Merge search results and seed repos, deduplicate by ID
    seen = {r["id"] for r in legacy_repos}
    for repo in seed_repos:
        if repo["id"] not in seen:
            legacy_repos.append(repo)
            seen.add(repo["id"])

    save(legacy_repos, "legacy_candidates.json")
    print("\nDone. Next step: run select_repos.py to apply stratified sampling.")