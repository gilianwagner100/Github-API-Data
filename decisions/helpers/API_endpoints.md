## Endpoints
- raw_repositories ← one row per repo, metadata snapshot
  -> https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#get-a-repository
    -> Values to keep:
        - id
        - name
        - owner.id (user id)
        - owner.login (profile name)
        - description
        - forks_count
        - stargazers_count
        - watchers_count
        - topics
        - created_at
        - pushed_at
        - load_timestamp (not in the API response)
- raw_star_history ← star activity (raw, no aggregates)
  -> https://docs.github.com/en/rest/activity/starring?apiVersion=2026-03-10 (inlcuding Header "Accept: application/vnd.github.star+json")
    -> Values to keep:
        - user.id (user id)
        - user.login (profile name)
        - starred_at
        - load_timestamp (not in the API response)
        - repo_id (not in the API response)
- raw_commit_activity ← commit activity (raw, no aggregates)
  -> Single Commits: https://docs.github.com/en/rest/commits/commits?apiVersion=2026-03-10
    -> Values to keep:
        - commit.author.date
        - author.id
        - author.login
        - committer.id
        - committer.login
        - load_timestamp (not in the API response)
        - repo_id (not in the API response)


## Rate Limits
- Primary Rate Limit: 5.000 requests per hour
- Secondary Rate Limit: Max. 900 points per minute for a single endpoint

- Checking Status of my rate limit:
    **x-ratelimit-remaining**	The number of requests remaining in the current rate limit window
    **x-ratelimit-used**	The number of requests you have made in the current rate limit window
    **x-ratelimit-reset**	The time at which the current rate limit window resets, in UTC epoch seconds