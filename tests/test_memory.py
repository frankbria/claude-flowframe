"""Tests for memory management."""

import tempfile
from pathlib import Path

import pytest

from claude_flowframe.memory import MemoryManager


@pytest.fixture
def temp_memory() -> MemoryManager:
    """Create a memory manager with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield MemoryManager(base_path=Path(tmpdir))


def test_store_and_query(temp_memory: MemoryManager) -> None:
    """Test storing and querying values."""
    temp_memory.store("test_key", "test_value", "test_ns")
    result = temp_memory.query("test_key", "test_ns")
    assert result == "test_value"


def test_query_nonexistent(temp_memory: MemoryManager) -> None:
    """Test querying a non-existent key."""
    result = temp_memory.query("nonexistent", "test_ns")
    assert result is None


def test_list_keys(temp_memory: MemoryManager) -> None:
    """Test listing keys in a namespace."""
    temp_memory.store("key1", "value1", "test_ns")
    temp_memory.store("key2", "value2", "test_ns")

    keys = temp_memory.list_keys("test_ns")
    assert sorted(keys) == ["key1", "key2"]


def test_delete(temp_memory: MemoryManager) -> None:
    """Test deleting a key."""
    temp_memory.store("test_key", "test_value", "test_ns")
    deleted = temp_memory.delete("test_key", "test_ns")
    assert deleted is True

    result = temp_memory.query("test_key", "test_ns")
    assert result is None


def test_metadata(temp_memory: MemoryManager) -> None:
    """Test storing and retrieving metadata."""
    metadata = {"author": "test", "timestamp": "2025-12-26"}
    temp_memory.store("test_key", "test_value", "test_ns", metadata)

    result_metadata = temp_memory.get_metadata("test_key", "test_ns")
    assert result_metadata == metadata
