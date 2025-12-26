"""Command-line interface for claude-flowframe."""

import json
import sys

import click
from rich.console import Console

from claude_flowframe import __version__
from claude_flowframe.hooks import HooksManager
from claude_flowframe.memory import MemoryManager
from claude_flowframe.swarm import SwarmOrchestrator

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="claude-flowframe")
def cli() -> None:
    """Claude FlowFrame - Minimal agentic orchestration framework."""
    pass


@cli.group()
def memory() -> None:
    """Memory management commands."""
    pass


@memory.command()
@click.argument("key")
@click.argument("value")
@click.option("--namespace", default="default", help="Memory namespace")
@click.option("--metadata", default="{}", help="JSON metadata")
def store(key: str, value: str, namespace: str, metadata: str) -> None:
    """Store a value in memory."""
    manager = MemoryManager()

    try:
        metadata_dict = json.loads(metadata)
    except json.JSONDecodeError:
        console.print("[red]Error: Invalid JSON metadata[/red]")
        sys.exit(1)

    manager.store(key, value, namespace, metadata_dict)
    console.print(f"[green]Stored:[/green] {key} in namespace '{namespace}'")


@memory.command()
@click.argument("key")
@click.option("--namespace", default="default", help="Memory namespace")
@click.option("--format", "output_format", default="text", help="Output format (text, json)")
def query(key: str, namespace: str, output_format: str) -> None:
    """Query a value from memory."""
    manager = MemoryManager()
    value = manager.query(key, namespace)

    if value is None:
        console.print(f"[yellow]Key not found:[/yellow] {key}")
        sys.exit(1)

    if output_format == "json":
        print(json.dumps({"key": key, "value": value, "namespace": namespace}))
    else:
        print(value)


@memory.command(name="list")
@click.option("--namespace", default="default", help="Memory namespace")
def list_keys(namespace: str) -> None:
    """List all keys in a namespace."""
    manager = MemoryManager()
    keys = manager.list_keys(namespace)

    if not keys:
        console.print(f"[yellow]No keys in namespace '{namespace}'[/yellow]")
    else:
        console.print(f"[green]Keys in '{namespace}':[/green]")
        for key in keys:
            console.print(f"  - {key}")


@memory.command()
@click.argument("key")
@click.option("--namespace", default="default", help="Memory namespace")
def delete(key: str, namespace: str) -> None:
    """Delete a key from memory."""
    manager = MemoryManager()
    deleted = manager.delete(key, namespace)

    if deleted:
        console.print(f"[green]Deleted:[/green] {key}")
    else:
        console.print(f"[yellow]Key not found:[/yellow] {key}")


@cli.group()
def swarm() -> None:
    """Swarm orchestration commands."""
    pass


@swarm.command()
@click.option("--topology", default="auto", help="Swarm topology (hierarchical, mesh, auto)")
@click.option("--max-agents", default=5, help="Maximum number of agents")
@click.option("--namespace", required=True, help="Swarm namespace")
def init(topology: str, max_agents: int, namespace: str) -> None:
    """Initialize a new swarm."""
    orchestrator = SwarmOrchestrator()
    orchestrator.init(namespace, topology, max_agents)
    console.print(f"[green]Initialized swarm:[/green] {namespace} (topology: {topology})")


@swarm.command()
@click.option("--objective", required=True, help="Task objective")
@click.option("--strategy", default="development", help="Execution strategy")
@click.option("--agents", required=True, help="Comma-separated agent roles")
@click.option("--namespace", required=True, help="Swarm namespace")
@click.option("--parallel", is_flag=True, help="Run agents in parallel")
def spawn(objective: str, strategy: str, agents: str, namespace: str, parallel: bool) -> None:
    """Spawn agents to execute a task."""
    orchestrator = SwarmOrchestrator()

    try:
        orchestrator.spawn(namespace, objective, strategy, agents, parallel)
        console.print(f"[green]Spawned agents in:[/green] {namespace}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@swarm.command()
@click.option("--namespace", required=True, help="Swarm namespace")
@click.option("--json", "json_output", is_flag=True, help="Output JSON")
def status(namespace: str, json_output: bool) -> None:
    """Get swarm status."""
    orchestrator = SwarmOrchestrator()
    result = orchestrator.status(namespace, json_output)

    if json_output:
        print(result)
    else:
        if isinstance(result, dict):
            status_val = result.get("status", "unknown")
            if status_val == "not_found":
                console.print(f"[yellow]Swarm not found:[/yellow] {namespace}")
            else:
                console.print(f"[green]Status:[/green] {status_val}")
                console.print(f"[blue]Namespace:[/blue] {namespace}")


@cli.group()
def hooks() -> None:
    """Hooks management commands."""
    pass


@hooks.command()
@click.option("--description", required=True, help="Task description")
@click.option("--session-id", required=True, help="Session ID")
def pre_task(description: str, session_id: str) -> None:
    """Execute pre-task hook."""
    manager = HooksManager()
    manager.pre_task(description, session_id)
    console.print(f"[green]Pre-task hook executed:[/green] {session_id}")


@hooks.command()
@click.option("--task-id", required=True, help="Task ID")
@click.option("--export-metrics", is_flag=True, help="Export metrics")
def post_task(task_id: str, export_metrics: bool) -> None:
    """Execute post-task hook."""
    manager = HooksManager()
    manager.post_task(task_id, export_metrics)
    console.print(f"[green]Post-task hook executed:[/green] {task_id}")


@hooks.command()
@click.option("--session-id", required=True, help="Session ID")
@click.option("--export-metrics", is_flag=True, help="Export metrics")
def session_end(session_id: str, export_metrics: bool) -> None:
    """Execute session-end hook."""
    manager = HooksManager()
    manager.session_end(session_id, export_metrics)
    console.print(f"[green]Session-end hook executed:[/green] {session_id}")


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
