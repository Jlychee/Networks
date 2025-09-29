from typing import Any

import aiohttp

from config import BASE_URL, HEADERS


async def get_all_repos(session: aiohttp.ClientSession, org: str | None) -> list[str]:
    repos = []
    page = 1
    while True:
        url = f"{BASE_URL}/orgs/{org}/repos?per_page=100&page={page}"
        async with session.get(url) as response:
            if response.status != 200:
                raise RuntimeError(f"Ошибка получения репозиториев: {response.status}")
            data = await response.json()

        if not data:
            break

        repos.extend([r['name'] for r in data if not r['archived']])
        page += 1
    return repos


async def get_commits(org: str | None, repo: str, session: aiohttp.ClientSession, page: int = 1) -> Any:
    url = f"{BASE_URL}/repos/{org}/{repo}/commits?per_page=100&page={page}"
    async with session.get(url, headers=HEADERS) as response:
        if response.status != 200:
            print(f"Ошибка получения коммитов {repo}: {response.status}")
            return {}
        return await response.json()


async def get_rate_limit(session: aiohttp.ClientSession) -> Any:
    async with session.get(f"{BASE_URL}/rate_limit", headers=HEADERS) as response:
        return await response.json()
