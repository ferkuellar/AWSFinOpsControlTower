from rich.console import Console
from rich.table import Table

from aws_clients import client

console = Console()


def scan_lambda_functions(profile: str, region: str):
    lamb = client("lambda", profile, region)
    functions = []

    try:
        response = lamb.list_functions()
    except Exception as error:
        console.print(f"[yellow]Lambda scan skipped in {region}: {error}[/yellow]")
        return functions

    table = Table(title=f"Lambda Functions | {region}")
    table.add_column("Region", style="magenta")
    table.add_column("Function", style="cyan")
    table.add_column("Runtime")
    table.add_column("Memory MB", justify="right")
    table.add_column("Timeout Sec", justify="right")
    table.add_column("Recommendation", style="bold")

    for fn in response.get("Functions", []):
        name = fn.get("FunctionName", "UNKNOWN")
        runtime = fn.get("Runtime", "UNKNOWN")
        memory = fn.get("MemorySize", 0)
        timeout = fn.get("Timeout", 0)

        recommendation = "KEEP"

        if memory >= 1024:
            recommendation = "REVIEW MEMORY SIZE"
        elif timeout >= 60:
            recommendation = "REVIEW TIMEOUT"

        item = {
            "region": region,
            "name": name,
            "runtime": runtime,
            "memory": memory,
            "timeout": timeout,
            "recommendation": recommendation,
        }

        functions.append(item)

        table.add_row(
            region,
            name,
            runtime,
            str(memory),
            str(timeout),
            recommendation,
        )

    console.print(table)
    return functions