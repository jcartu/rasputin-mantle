"""
Atomic state persistence for Rasputin Mantle orchestrator.

This module provides crash-safe state management using atomic write semantics:
write to temporary file → fsync → atomic rename. This guarantees that the state
file is never left in a partially-written state, even if the process crashes
during a save operation.

The State class wraps a JSON state file and provides dict-like access with
automatic persistence. All writes are atomic at the filesystem level.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class State:
    """
    Manages orchestrator state with atomic, crash-safe persistence.

    Wraps a JSON state file and provides dict-like access. All save operations
    are atomic: write to temporary file, fsync, then atomic rename.

    Attributes:
        path: Path to the state JSON file.
        _data: In-memory state dictionary.
    """

    def __init__(self, path: str) -> None:
        """
        Initialize State with a path to the state file.

        Args:
            path: Path to the JSON state file. File need not exist initially.
        """
        self.path = Path(path)
        self._data: dict[str, Any] = {}

    def load(self) -> None:
        """
        Load state from the JSON file.

        If the file does not exist, initializes an empty state dictionary.
        If the file exists but is invalid JSON, raises json.JSONDecodeError.
        """
        if self.path.exists():
            with open(self.path, "r") as f:
                self._data = json.load(f)
        else:
            self._data = {}

    def save(self) -> None:
        """
        Save state to the JSON file atomically.

        Writes to a temporary file, calls fsync() to ensure data is written to
        disk, then atomically renames the temporary file to the target path.
        This guarantees the state file is never left in a partially-written state.
        """
        # Ensure parent directory exists
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file
        tmp_path = Path(str(self.path) + ".tmp")
        with open(tmp_path, "w") as f:
            json.dump(self._data, f)
            # Ensure data is written to disk
            os.fsync(f.fileno())

        # Atomically replace the target file
        os.replace(tmp_path, self.path)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from state by key.

        Args:
            key: The state key.
            default: Value to return if key is not found.

        Returns:
            The value associated with the key, or default if not found.
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in state.

        Args:
            key: The state key.
            value: The value to set.
        """
        self._data[key] = value

    def update(self, data: dict[str, Any]) -> None:
        """
        Update state with multiple key-value pairs.

        Args:
            data: Dictionary of key-value pairs to merge into state.
        """
        self._data.update(data)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a copy of the state dictionary.

        Returns:
            A shallow copy of the internal state dictionary.
        """
        return self._data.copy()

    def __repr__(self) -> str:
        """Return a string representation of the State object."""
        return f"State(path={self.path!r}, data={self._data!r})"
