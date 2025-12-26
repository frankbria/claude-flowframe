"""Hooks system for workflow lifecycle events."""

import json
import subprocess
from pathlib import Path
from typing import Optional


class HooksManager:
    """Manages workflow lifecycle hooks."""

    def __init__(self, base_path: Optional[Path] = None) -> None:
        """Initialize hooks manager.

        Args:
            base_path: Base directory for hooks. Defaults to ~/.claude-flowframe/hooks
        """
        self.base_path = base_path or Path.home() / ".claude-flowframe" / "hooks"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.log_path = self.base_path / "logs"
        self.log_path.mkdir(parents=True, exist_ok=True)

    def _get_hook_log_path(self, hook_type: str, session_id: str) -> Path:
        """Get the log file path for a hook execution."""
        return self.log_path / f"{session_id}_{hook_type}.json"

    def pre_task(self, description: str, session_id: str) -> None:
        """Execute pre-task hook.

        Args:
            description: Description of the task
            session_id: Session identifier
        """
        log_data = {
            "hook_type": "pre-task",
            "description": description,
            "session_id": session_id,
        }

        log_path = self._get_hook_log_path("pre-task", session_id)
        log_path.write_text(json.dumps(log_data, indent=2))

        # Execute custom pre-task script if it exists
        script_path = self.base_path / "pre-task.sh"
        if script_path.exists():
            self._execute_script(script_path, session_id)

    def post_task(self, task_id: str, export_metrics: bool = False) -> None:
        """Execute post-task hook.

        Args:
            task_id: Task identifier
            export_metrics: Whether to export metrics
        """
        log_data = {
            "hook_type": "post-task",
            "task_id": task_id,
            "export_metrics": export_metrics,
        }

        log_path = self._get_hook_log_path("post-task", task_id)
        log_path.write_text(json.dumps(log_data, indent=2))

        # Execute custom post-task script if it exists
        script_path = self.base_path / "post-task.sh"
        if script_path.exists():
            self._execute_script(script_path, task_id, export_metrics=export_metrics)

    def session_end(self, session_id: str, export_metrics: bool = False) -> None:
        """Execute session-end hook.

        Args:
            session_id: Session identifier
            export_metrics: Whether to export metrics
        """
        log_data = {
            "hook_type": "session-end",
            "session_id": session_id,
            "export_metrics": export_metrics,
        }

        log_path = self._get_hook_log_path("session-end", session_id)
        log_path.write_text(json.dumps(log_data, indent=2))

        # Execute custom session-end script if it exists
        script_path = self.base_path / "session-end.sh"
        if script_path.exists():
            self._execute_script(script_path, session_id, export_metrics=export_metrics)

    def _execute_script(
        self, script_path: Path, session_id: str, export_metrics: bool = False
    ) -> None:
        """Execute a hook script.

        Args:
            script_path: Path to the script
            session_id: Session identifier
            export_metrics: Whether to export metrics
        """
        env = {
            "CLAUDE_FLOWFRAME_SESSION_ID": session_id,
            "CLAUDE_FLOWFRAME_EXPORT_METRICS": str(export_metrics),
        }

        try:
            subprocess.run(
                [str(script_path)],
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            # Log error but don't fail the workflow
            error_log = self.log_path / f"error_{session_id}.txt"
            error_log.write_text(
                f"Script: {script_path}\n"
                f"Exit Code: {e.returncode}\n"
                f"Stdout: {e.stdout}\n"
                f"Stderr: {e.stderr}\n"
            )
