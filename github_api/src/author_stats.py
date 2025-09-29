from collections import Counter
from datetime import datetime
from typing import Any


class AuthorStats:
    def __init__(self) -> None:
        self.total_commits = 0
        self.repos: set[str] = set()
        self.lines_changed = 0
        self.merge_commits = 0
        self.dates: list[datetime] = []
        self.month_counter: Counter[str] = Counter()
        self.repo_commits: Counter[str] = Counter()
        self.commits: list[dict[str, Any]] = []

    def add_commit(self, repo: str, commit_data: dict[str, Any]) -> None:
        self.total_commits += 1
        self.repos.add(repo)
        self.repo_commits[repo] += 1

        date_str = commit_data['commit']['author']['date']
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        self.dates.append(dt)
        self.month_counter[dt.strftime("%Y-%m")] += 1

        message = commit_data['commit']['message']
        if message.startswith("Merge pull request #"):
            self.merge_commits += 1

        stats = commit_data.get('stats')
        if stats:
            self.lines_changed += len(stats['additions']) + len(stats['deletions'])

        self.commits.append(commit_data)

    def merge(self, other: "AuthorStats") -> None:
        self.total_commits += other.total_commits
        self.repos.update(other.repos)
        self.lines_changed += other.lines_changed
        self.merge_commits += other.merge_commits
        self.dates.extend(other.dates)
        self.month_counter.update(other.month_counter)
        self.repo_commits.update(other.repo_commits)
        self.commits.extend(other.commits)
