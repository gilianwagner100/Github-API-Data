import json
import os
from datetime import datetime, timezone
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_DIR  = "raw_data"
OUTPUT_DIR = "raw_data"

# How many repos to keep per star bucket per cohort.
# 10 per bucket * 4 buckets = up to 40 repos per cohort — enough for
# Mann-Whitney U (recommended n ≥ 20 per group) without overloading the API.
REPOS_PER_BUCKET = 10

STAR_BUCKETS = [
    (500,    2_000,  "500-2k"),
    (2_001,  10_000, "2k-10k"),
    (10_001, 50_000, "10k-50k"),
    (50_001, 10**9,  "50k+"),
]

# Repos to always exclude regardless of filters — edge cases that would contaminate cohort boundaries
EXCLUSION_LIST = {
    # Transformers predates the hype wave but is central to LLM tooling.
    "huggingface/transformers",
}

# Helpers
def load(filename: str) -> list[dict]:
    path = os.path.join(INPUT_DIR, filename)
    with open(path) as f:
        return json.load(f)


def save(data: list[dict], filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Saved {len(data)} repos → {path}")


def star_bucket(stars: int) -> str | None:
    for lo, hi, label in STAR_BUCKETS:
        if lo <= stars <= hi:
            return label
    return None


def repo_age_months(created_at: str) -> float:
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return (now - created).days / 30.44


def extract_fields(repo: dict, cohort: str) -> dict:
    """Slim down the raw GitHub API object to only the fields we need."""
    return {
        "id":           repo["id"],
        "full_name":    repo["full_name"],
        "cohort":       cohort,
        "created_at":   repo["created_at"],
        "stars":        repo["stargazers_count"],
        "forks":        repo["forks_count"],
        "open_issues":  repo["open_issues_count"],
        "archived":     repo["archived"],
        "language":     repo.get("language"),
        "topics":       repo.get("topics", []),
        "description":  repo.get("description", ""),
        "html_url":     repo["html_url"],
        "age_months":   round(repo_age_months(repo["created_at"]), 1),
        "star_bucket":  star_bucket(repo["stargazers_count"]),
    }


# Inclusion criteria
def passes_filters(repo: dict, log: list[str]) -> bool:
    name = repo.get("full_name", "")

    if name in EXCLUSION_LIST:
        log.append(f"EXCLUDE (exclusion list)       {name}")
        return False

    if repo.get("fork"):
        log.append(f"EXCLUDE (is a fork)            {name}")
        return False

    if repo.get("archived"):
        # Exclude archived repos
        log.append(f"EXCLUDE (archived)             {name}")
        return False

    if repo.get("language") != "Python":
        log.append(f"EXCLUDE (language={repo.get('language')}) {name}")
        return False

    stars = repo.get("stargazers_count", 0)
    if stars < 500:
        log.append(f"EXCLUDE (stars={stars} < 500)  {name}")
        return False

    age = repo_age_months(repo["created_at"])
    if age < 6:
        log.append(f"EXCLUDE (age={age:.1f}mo < 6)  {name}")
        return False

    log.append(f"INCLUDE                        {name}  (stars={stars}, age={age:.1f}mo)")
    return True


# Stratified sampling
def stratified_sample(repos: list[dict], n_per_bucket: int) -> list[dict]:
    """
    Group passing repos into star buckets, then take the top n_per_bucket
    from each bucket sorted by stars descending.
    """
    buckets = defaultdict(list)
    for repo in repos:
        bucket = star_bucket(repo["stargazers_count"])
        if bucket:
            buckets[bucket].append(repo)

    selected = []
    for _, _, label in STAR_BUCKETS:
        bucket_repos = sorted(buckets[label], key=lambda r: r["stargazers_count"], reverse=True)
        chosen = bucket_repos[:n_per_bucket]
        selected.extend(chosen)
        print(f"  Bucket {label:10s}: {len(bucket_repos):3d} candidates → kept {len(chosen)}")

    return selected


# Main
def select_cohort(filename: str, cohort: str, log: list[str]) -> list[dict]:
    log.append(f"\n{'='*60}")
    log.append(f"COHORT: {cohort}")
    log.append(f"{'='*60}")

    raw = load(filename)
    log.append(f"Raw candidates: {len(raw)}")

    passing = [r for r in raw if passes_filters(r, log)]
    log.append(f"\nPassing filters: {len(passing)}")

    print(f"\n{cohort}: {len(raw)} candidates → {len(passing)} pass filters")
    print(f"Stratified sampling ({REPOS_PER_BUCKET} per bucket):")
    sampled = stratified_sample(passing, REPOS_PER_BUCKET)

    return [extract_fields(r, cohort) for r in sampled]


if __name__ == "__main__":
    log_lines = [f"Selection run: {datetime.now().isoformat()}"]

    llm_repos    = select_cohort("llm_candidates.json",    "llm_agentic", log_lines)
    legacy_repos = select_cohort("legacy_candidates.json", "legacy_ml",   log_lines)

    save(llm_repos,    "llm_selected.json")
    save(legacy_repos, "legacy_selected.json")

    log_path = os.path.join(OUTPUT_DIR, "selection_log.txt")
    with open(log_path, "w") as f:
        f.write("\n".join(log_lines))
    print(f"\nAudit log → {log_path}")

    # Print summary
    print(f"\n{'='*40}")
    print(f"Final dataset:")
    print(f"  LLM/Agentic AI repos : {len(llm_repos)}")
    print(f"  Legacy ML repos      : {len(legacy_repos)}")
    print(f"  Total                : {len(llm_repos) + len(legacy_repos)}")

    # Bucket distribution
    for cohort_name, repos in [("LLM", llm_repos), ("Legacy", legacy_repos)]:
        counts = defaultdict(int)
        for r in repos:
            counts[r["star_bucket"]] += 1
        print(f"\n  {cohort_name} bucket distribution: {dict(counts)}")
