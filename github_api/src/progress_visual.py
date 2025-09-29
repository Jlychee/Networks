import json
import os
from typing import Any, Callable

from rich import box
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from author_stats import AuthorStats


def show_author_selection_progress(
    selected_authors: list[str],
    total_emails: dict[str, AuthorStats],
    finalize_stats: Callable[[dict[str, AuthorStats]], dict[str, Any]],
) -> None:
    os.makedirs("../authors_info", exist_ok=True)
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Сбор детальной статистики:"),
        BarColumn(bar_width=40, complete_style="green"),
        TextColumn("[yellow]{task.completed}/{task.total}"),
    ) as progress:
        task = progress.add_task("", total=len(selected_authors))
        for email in selected_authors:
            stats = total_emails[email]
            data = finalize_stats({email: stats})[email]
            safe_name = email.replace("@", "_at_").replace(".", "_")
            with open(f"../authors_info/{safe_name}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            progress.update(task, advance=1)


def show_single_author_activity(email: str, stats: "AuthorStats") -> None:
    console = Console()
    console.print(f"\n[bold cyan]{email}[/bold cyan] — Активность по месяцам:")

    months = sorted(stats.month_counter.keys())

    if not months:
        console.print("[yellow]Нет данных по месяцам[/]")
        return

    values = [stats.month_counter[m] for m in months]
    max_value = max(values) if values else 1

    table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE, title="Коммиты по месяцам")
    table.add_column("Месяц", justify="center")
    table.add_column("Коммиты", justify="right")
    table.add_column("График", justify="left")

    for month, count in zip(months, values):
        bar = "█" * int(count / max_value * 20)
        table.add_row(month, str(count), bar)

    console.print(table)
