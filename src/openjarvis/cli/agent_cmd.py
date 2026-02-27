"""``jarvis agent`` — agent lifecycle management."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table


@click.group()
def agent() -> None:
    """Manage agents — list, spawn, kill, info."""


@agent.command("list")
def list_agents() -> None:
    """List available agent types and running agents."""
    console = Console(stderr=True)

    # List registered agent types
    try:
        import openjarvis.agents  # noqa: F401 -- trigger registration
        from openjarvis.core.registry import AgentRegistry

        table = Table(title="Registered Agent Types")
        table.add_column("Key", style="cyan")
        table.add_column("Class", style="green")
        table.add_column("Accepts Tools", style="yellow")

        for key in sorted(AgentRegistry.keys()):
            cls = AgentRegistry.get(key)
            accepts = "Yes" if getattr(cls, "accepts_tools", False) else "No"
            table.add_row(key, cls.__name__, accepts)

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error listing agents: {exc}[/red]")

    # List running agents from agent_tools if available
    try:
        from openjarvis.tools.agent_tools import _SPAWNED_AGENTS

        if _SPAWNED_AGENTS:
            table2 = Table(title="Running Agents")
            table2.add_column("ID", style="cyan")
            table2.add_column("Type", style="green")
            table2.add_column("Status", style="yellow")
            for aid, info in _SPAWNED_AGENTS.items():
                table2.add_row(aid, info.get("agent_type", ""), info.get("status", ""))
            console.print(table2)
    except ImportError:
        pass


@agent.command()
@click.argument("agent_key")
def info(agent_key: str) -> None:
    """Show detailed info about an agent type."""
    console = Console(stderr=True)
    try:
        import openjarvis.agents  # noqa: F401 -- trigger registration
        from openjarvis.core.registry import AgentRegistry

        if not AgentRegistry.contains(agent_key):
            console.print(f"[red]Unknown agent: {agent_key}[/red]")
            return

        cls = AgentRegistry.get(agent_key)
        console.print(f"[bold]{agent_key}[/bold] — {cls.__name__}")
        console.print(f"  Module: {cls.__module__}")
        console.print(f"  Accepts tools: {getattr(cls, 'accepts_tools', False)}")
        if cls.__doc__:
            console.print(f"  Description: {cls.__doc__.strip().splitlines()[0]}")
    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")


__all__ = ["agent"]
