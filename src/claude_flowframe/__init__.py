"""Claude FlowFrame - Minimal agentic orchestration framework for Claude Code."""

__version__ = "0.1.0"

from claude_flowframe.hooks import HooksManager
from claude_flowframe.memory import MemoryManager
from claude_flowframe.swarm import SwarmOrchestrator

__all__ = ["MemoryManager", "SwarmOrchestrator", "HooksManager", "__version__"]
