from config import GITHUB_BASE_URL, HEADERS, LEGACY_REPOS, LLM_REPOS
import requests
import time
from datetime import datetime, timezone

def get_repository_data(repository:str, max_retries:int = 5) -> dict:
    """GET request for repository endpoint with rate limit handling."""
    url = f"{GITHUB_BASE_URL}/repos/{repository}"

    wait_time = 60 # required wait time of 60 seconds as per API doc

    for attempt in range(max_retries):
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 403:
            retry_after = response.headers.get("retry-after")

            if retry_after:
                print(f"Rate limited. Waiting for {retry_after}s (retry-after) ...")
                time.sleep(int(retry_after))
            
            elif response.headers.get("x-ratelimit-remaining") == "0":
                time_reset = int(response.headers.get("x-ratelimit-reset"))
                time_now = time.time()
                sleep_for = max(time_reset - time_now, 0)

                print(f"Rate limited & will reset at {time_reset}. Sleeping for {sleep_for}s ...")
                time.sleep(sleep_for)

            else:
                if attempt >= max_retries -1:
                    raise Exception(f"Secondary Rate Limit: max retries {max_retries} exceeded.")
                print(f"Secondary rate limit: waiting for {wait_time}s (attempt {attempt + 1})")
                time.sleep(wait_time)
                wait_time *= 2 # exponential backoff when secondary rate limit is reached as per API doc

        else:
            print(f"HTTP Response Code '{response.status_code} on {url}'")
    
    return {}