from typing import Any

from author_stats import AuthorStats


def finalize_stats(authors: dict[str, AuthorStats]) -> dict[str, Any]:
    result = {}

    for email, stats in authors.items():
        if not stats.dates:
            continue

        first_commit = min(stats.dates)
        last_commit = max(stats.dates)

        dates = sorted(stats.dates)
        intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        avg_interval = sum(intervals) / len(intervals)

        most_active_month = stats.month_counter.most_common(1)[0]
        most_active_repo = stats.repo_commits.most_common(1)[0]

        result[email] = {
            "email": email,
            "commits": stats.total_commits,
            "repos": len(stats.repos),
            "avg_commit_size": round(stats.lines_changed / stats.total_commits, 2) if stats.total_commits else 0,
            "merge_commits": stats.merge_commits,
            "first_commit": first_commit.date().isoformat(),
            "last_commit": last_commit.date().isoformat(),
            "avg_interval_days": round(avg_interval, 2),
            "most_active_month": most_active_month,
            "repos_list": list(stats.repos),
            "most_active_repo": most_active_repo,
        }
    return result
