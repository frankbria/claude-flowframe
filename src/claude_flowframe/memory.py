"""Memory management system for workflow state persistence."""

import json
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    """A single memory entry with metadata."""

    key: str
    value: str
    namespace: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryManager:
    """Manages key-value storage with namespace support."""

    def __init__(self, base_path: Optional[Path] = None) -> None:
        """Initialize memory manager.

        Args:
            base_path: Base directory for memory storage. Defaults to ~/.claude-flowframe/memory
        """
        self.base_path = base_path or Path.home() / ".claude-flowframe" / "memory"
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_namespace_path(self, namespace: str) -> Path:
        """Get the directory path for a namespace."""
        ns_path = self.base_path / namespace
        ns_path.mkdir(parents=True, exist_ok=True)
        return ns_path

    def _get_entry_path(self, namespace: str, key: str) -> Path:
        """Get the file path for a specific key."""
        ns_path = self._get_namespace_path(namespace)
        # Use safe filename: replace / with _
        safe_key = key.replace("/", "_")
        return ns_path / f"{safe_key}.json"

    def store(
        self, key: str, value: str, namespace: str = "default", metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """Store a value in memory.

        Args:
            key: The key to store under
            value: The value to store
            namespace: The namespace to store in
            metadata: Optional metadata dictionary
        """
        entry = MemoryEntry(
            key=key, value=value, namespace=namespace, metadata=metadata or {}
        )

        entry_path = self._get_entry_path(namespace, key)

        # Atomic write
        temp_path = entry_path.with_suffix(".tmp")
        temp_path.write_text(entry.model_dump_json(indent=2))
        temp_path.replace(entry_path)

    def query(self, key: str, namespace: str = "default") -> Optional[str]:
        """Query a value from memory.

        Args:
            key: The key to query
            namespace: The namespace to query from

        Returns:
            The stored value, or None if not found
        """
        entry_path = self._get_entry_path(namespace, key)

        if not entry_path.exists():
            return None

        try:
            data = json.loads(entry_path.read_text())
            entry = MemoryEntry.model_validate(data)
            return entry.value
        except (json.JSONDecodeError, ValueError):
            return None

    def list_keys(self, namespace: str = "default") -> list[str]:
        """List all keys in a namespace.

        Args:
            namespace: The namespace to list

        Returns:
            List of keys in the namespace
        """
        ns_path = self._get_namespace_path(namespace)
        keys = []

        for entry_file in ns_path.glob("*.json"):
            try:
                data = json.loads(entry_file.read_text())
                entry = MemoryEntry.model_validate(data)
                keys.append(entry.key)
            except (json.JSONDecodeError, ValueError):
                continue

        return sorted(keys)

    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete a key from memory.

        Args:
            key: The key to delete
            namespace: The namespace to delete from

        Returns:
            True if deleted, False if key didn't exist
        """
        entry_path = self._get_entry_path(namespace, key)

        if entry_path.exists():
            entry_path.unlink()
            return True
        return False

    def get_metadata(self, key: str, namespace: str = "default") -> Optional[dict[str, Any]]:
        """Get metadata for a key.

        Args:
            key: The key to get metadata for
            namespace: The namespace to query from

        Returns:
            The metadata dictionary, or None if not found
        """
        entry_path = self._get_entry_path(namespace, key)

        if not entry_path.exists():
            return None

        try:
            data = json.loads(entry_path.read_text())
            entry = MemoryEntry.model_validate(data)
            return entry.metadata
        except (json.JSONDecodeError, ValueError):
            return None
