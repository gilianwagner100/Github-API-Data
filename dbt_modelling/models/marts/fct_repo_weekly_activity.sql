{{ config(materialized='table') }}

with repos as (
    select repo_id, created_at
    from {{ ref('dim_repositories') }}
),

max_week as (
    select
        repo_id,
        created_at,
        least(104, cast(floor(timestamp_diff(current_timestamp(), created_at, day) / 7) as int64)) as max_age_weeks
    from repos
),

spine as (
    select
        repo_id,
        created_at,
        week_number
    from max_week,
    unnest(generate_array(0, max_age_weeks)) as week_number
),

star_events as (
    select
        s.repo_id,
        cast(floor(timestamp_diff(s.starred_at, r.created_at, day) / 7) as int64) as week_number
    from {{ ref('stg_star_history') }} s
    inner join repos r on s.repo_id = r.repo_id
    where s.starred_at >= r.created_at
),

weekly_stars as (
    select repo_id, week_number, count(*) as weekly_stars
    from star_events
    group by repo_id, week_number
),

commit_events as (
    select
        c.repo_id,
        cast(floor(timestamp_diff(c.committed_at, r.created_at, day) / 7) as int64) as week_number
    from {{ ref('stg_commits') }} c
    inner join repos r on c.repo_id = r.repo_id
    where c.committed_at >= r.created_at
),

weekly_commits as (
    select repo_id, week_number, count(*) as weekly_commits
    from commit_events
    group by repo_id, week_number
),

joined as (
    select
        spine.repo_id,
        spine.week_number as repo_age_weeks,
        timestamp_add(spine.created_at, interval spine.week_number * 7 day) as week_start_date,
        coalesce(ws.weekly_stars, 0) as weekly_stars,
        coalesce(wc.weekly_commits, 0) as weekly_commits
    from spine
    left join weekly_stars ws
        on spine.repo_id = ws.repo_id and spine.week_number = ws.week_number
    left join weekly_commits wc
        on spine.repo_id = wc.repo_id and spine.week_number = wc.week_number
),

with_cumulative as (
    select
        *,
        sum(weekly_stars) over (partition by repo_id order by repo_age_weeks) as cumulative_stars,
        sum(weekly_commits) over (partition by repo_id order by repo_age_weeks) as cumulative_commits
    from joined
)

select
    *,
    safe_divide(cumulative_commits, cumulative_stars) as commit_to_star_ratio
from with_cumulative
order by repo_id, repo_age_weeks