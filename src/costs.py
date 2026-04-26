from datetime import date
from rich.console import Console
from rich.table import Table

from aws_clients import global_client

console = Console()


def get_monthly_cost_by_service(profile: str):
    ce = global_client("ce", profile)

    today = date.today()
    start = today.replace(day=1).isoformat()
    end = today.isoformat()

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": start,
            "End": end
        },
        Granularity="MONTHLY",
        Metrics=[
            "UnblendedCost"
        ],
        GroupBy=[
            {
                "Type": "DIMENSION",
                "Key": "SERVICE"
            }
        ],
    )

    table = Table(title=f"AWS Cost by Service | {start} to {end}")
    table.add_column("Service", style="cyan")
    table.add_column("Cost USD", justify="right", style="green")

    total = 0.0
    cost_items = []

    results = response.get("ResultsByTime", [])

    if not results:
        console.print("[yellow]No Cost Explorer results returned.[/yellow]")
        return {
            "start": start,
            "end": end,
            "total": total,
            "services": cost_items,
        }

    groups = results[0].get("Groups", [])

    for result in groups:
        service = result["Keys"][0]
        amount = float(
            result["Metrics"]["UnblendedCost"]["Amount"]
        )

        if amount > 0:
            total += amount

            item = {
                "service": service,
                "amount": round(amount, 4),
            }

            cost_items.append(item)

    cost_items = sorted(
        cost_items,
        key=lambda x: x["amount"],
        reverse=True
    )

    for item in cost_items:
        table.add_row(
            item["service"],
            f"${item['amount']:,.2f}"
        )

    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold yellow]${total:,.2f}[/bold yellow]"
    )

    console.print(table)

    return {
        "start": start,
        "end": end,
        "total": round(total, 4),
        "services": cost_items,
    }