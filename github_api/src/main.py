import asyncio
import time

from rich.console import Console
from rich.markup import escape
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import ORG
from finalize_stats import finalize_stats
from github_limit_extension import GitHubLimitExceeded
from progress_visual import show_author_selection_progress, show_single_author_activity
from services import process_all_repos

console = Console()


async def main() -> None:
    start = time.time()
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Сбор репозиториев и коммитов...\n"),
        transient=False,
    ) as progress:
        progress.add_task("", total=None)
        progress.start()
        try:
            total_emails = await process_all_repos(ORG)
        except GitHubLimitExceeded as e:
            progress.stop()
            console.print(f"[red]{e}[/red]")
            return

    top_100 = sorted(total_emails.items(), key=lambda x: x[1].total_commits - x[1].merge_commits, reverse=True)[:100]

    console.print("\n[bold cyan]Топ 100 самых активных авторов (без merge-коммитов):[/]\n")
    for i, (email, stats) in enumerate(top_100, 1):
        clean_commits = stats.total_commits - stats.merge_commits
        console.print(f"[yellow]{i}[/]. {email}: [green]{clean_commits}[/] коммитов")

    choice = int(
        input(
            "\nАктивность по месяцам какого из 100 пользователей вы хотите увидеть? "
            "(введите номер, или -1 чтобы пропустить):\n"
        )
    )

    if 1 <= choice <= 100:
        email, stats = top_100[choice - 1]
        console.print(f"\n[bold cyan]Активность пользователя {email} по месяцам:[/]")
        show_single_author_activity(email, stats)
    elif choice == -1:
        console.print("[yellow]Пропускаем отображение активности по месяцам[/]")
    else:
        console.print("[red]Неверный ввод, пропускаем...[/]")

    print(f"Прошло времени: {time.time() - start:.2f}")

    n = -1
    while n < 0 or n > 100:
        n = int(input("\nПодробную статистику по скольким авторам вы хотите собрать? (0-100):\n"))

    selected_authors = [email for email, _ in top_100[:n]]
    show_author_selection_progress(selected_authors, total_emails, finalize_stats)
    console.print("\n✅ [bold green]Детальная статистика сохранена в `authors_info/`[/]")


if __name__ == "__main__":
    asyncio.run(main())
