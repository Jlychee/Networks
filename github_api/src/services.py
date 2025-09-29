import asyncio
from collections import defaultdict

import aiohttp
from rich.progress import Progress, TaskID

from author_stats import AuthorStats
from config import HEADERS
from github_api import get_all_repos, get_commits, get_rate_limit
from github_limit_extension import GitHubLimitExceeded

sem = asyncio.Semaphore(10)


async def is_limit_over(session: aiohttp.ClientSession) -> bool:
    data = await get_rate_limit(session)
    core = data['rate']

    if core['remaining'] <= 1:
        raise GitHubLimitExceeded(
            f"Из {core['limit']} использовано {core['used']} запросов. " "Дальнейшая обработка невозможна!"
        )
    return False


async def process_all_repos(org: str | None) -> dict[str, AuthorStats]:
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
        await is_limit_over(session)

        all_repos = await get_all_repos(session, org)

        total_emails: dict[str, AuthorStats] = {}
        tasks = [get_authors_by_commit(org, repo, session) for repo in all_repos]

        for coro in asyncio.as_completed(tasks):
            repo_stats = await coro
            for email, stats in repo_stats.items():
                if email not in total_emails:
                    total_emails[email] = stats
                else:
                    total_emails[email].merge(stats)
        return total_emails


async def get_authors_by_commit(
    org: str | None,
    repo: str,
    session: aiohttp.ClientSession,
    progress: Progress | None = None,
    task_id: TaskID | None = None,
) -> dict[str, AuthorStats]:

    authors: dict[str, AuthorStats] = defaultdict(AuthorStats)
    page = 1

    async with sem:
        while True:
            commits = await get_commits(org, repo, session, page)
            if not commits:
                break

            for commit_data in commits:
                commit = commit_data.get('commit', {})
                author_email = commit.get('author', {}).get('email')
                if author_email:
                    authors[author_email].add_commit(repo, commit_data)
            page += 1
    if progress and task_id:
        progress.update(task_id, advance=1)
    return authors
