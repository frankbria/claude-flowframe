"""Swarm orchestration system using Claude Code's Task tool via MCP."""

import json
import subprocess
import time
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class Topology(str, Enum):
    """Swarm topology types."""

    HIERARCHICAL = "hierarchical"
    MESH = "mesh"
    AUTO = "auto"


class SwarmStatus(str, Enum):
    """Swarm execution status."""

    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SwarmConfig(BaseModel):
    """Configuration for a swarm instance."""

    namespace: str
    topology: Topology
    max_agents: int = 5
    objective: Optional[str] = None
    strategy: Optional[str] = None
    agents: list[str] = []


class SwarmOrchestrator:
    """Orchestrates multi-agent swarms using Claude Code via MCP."""

    def __init__(self, base_path: Optional[Path] = None) -> None:
        """Initialize swarm orchestrator.

        Args:
            base_path: Base directory for swarm storage. Defaults to ~/.claude-flowframe/swarms
        """
        self.base_path = base_path or Path.home() / ".claude-flowframe" / "swarms"
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_swarm_path(self, namespace: str) -> Path:
        """Get the directory path for a swarm namespace."""
        swarm_path = self.base_path / namespace
        swarm_path.mkdir(parents=True, exist_ok=True)
        return swarm_path

    def _get_config_path(self, namespace: str) -> Path:
        """Get the config file path for a swarm."""
        return self._get_swarm_path(namespace) / "config.json"

    def _get_status_path(self, namespace: str) -> Path:
        """Get the status file path for a swarm."""
        return self._get_swarm_path(namespace) / "status.json"

    def init(self, namespace: str, topology: str = "auto", max_agents: int = 5) -> None:
        """Initialize a new swarm.

        Args:
            namespace: Unique identifier for this swarm
            topology: Swarm topology (hierarchical, mesh, auto)
            max_agents: Maximum number of agents to spawn
        """
        config = SwarmConfig(
            namespace=namespace,
            topology=Topology(topology),
            max_agents=max_agents,
        )

        config_path = self._get_config_path(namespace)
        config_path.write_text(config.model_dump_json(indent=2))

        # Initialize status
        self._update_status(namespace, SwarmStatus.INITIALIZING)

    def spawn(
        self,
        namespace: str,
        objective: str,
        strategy: str = "development",
        agents: Optional[str] = None,
        parallel: bool = False,
    ) -> None:
        """Spawn agents to execute an objective.

        Args:
            namespace: The swarm namespace
            objective: The task objective
            strategy: Execution strategy (development, testing, etc.)
            agents: Comma-separated list of agent roles
            parallel: Whether to run agents in parallel (mesh) or sequential (hierarchical)
        """
        config_path = self._get_config_path(namespace)
        if not config_path.exists():
            raise ValueError(f"Swarm namespace '{namespace}' not initialized")

        config = SwarmConfig.model_validate_json(config_path.read_text())
        config.objective = objective
        config.strategy = strategy

        if agents:
            config.agents = [a.strip() for a in agents.split(",")]

        # Update config
        config_path.write_text(config.model_dump_json(indent=2))

        # Update status
        self._update_status(namespace, SwarmStatus.RUNNING)

        # For now, we simulate spawning by marking the tasks
        # In a full implementation, this would call Claude Code's Task tool via MCP
        swarm_path = self._get_swarm_path(namespace)

        for i, agent_role in enumerate(config.agents):
            task_file = swarm_path / f"task_{i}_{agent_role}.txt"
            task_file.write_text(
                f"Agent: {agent_role}\n"
                f"Objective: {objective}\n"
                f"Strategy: {strategy}\n"
                f"Status: pending\n"
            )

        # Mark as completed for now (would be async in real implementation)
        time.sleep(0.1)
        self._update_status(namespace, SwarmStatus.COMPLETED)

    def status(self, namespace: str, json_output: bool = False) -> dict[str, str] | str:
        """Get the status of a swarm.

        Args:
            namespace: The swarm namespace
            json_output: Whether to return JSON string

        Returns:
            Status dictionary or JSON string
        """
        status_path = self._get_status_path(namespace)

        if not status_path.exists():
            return {"status": "not_found"} if not json_output else '{"status": "not_found"}'

        status_data = json.loads(status_path.read_text())

        if json_output:
            return json.dumps(status_data)

        return status_data

    def _update_status(self, namespace: str, status: SwarmStatus) -> None:
        """Update the status of a swarm."""
        status_path = self._get_status_path(namespace)
        status_data = {
            "status": status.value,
            "timestamp": time.time(),
            "namespace": namespace,
        }
        status_path.write_text(json.dumps(status_data, indent=2))
