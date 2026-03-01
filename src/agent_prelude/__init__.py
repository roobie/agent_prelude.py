"""agent_prelude package

This module provides a small set of helper utilities commonly used by
small automation scripts and testing harnesses. The functions are intentionally
minimal and aim to be easy to test.
"""

from __future__ import annotations

import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Union

import requests

PathLike = Union[str, Path]


# Filesystem operations
def read(path: PathLike, format: str = "auto") -> Any:
    """Read a file and return its contents.

    - If ``format == 'json'`` the content is parsed as JSON and the resulting
      Python object is returned.
    - If ``format == 'auto'`` and the path ends with ``.json`` the file is
      parsed as JSON.
    - Otherwise the raw text content (str) is returned.

    Raises: ``FileNotFoundError``, ``JSONDecodeError`` on invalid JSON.
    """
    p = Path(path).expanduser()
    content = p.read_text(encoding="utf-8")
    if format == "json" or (format == "auto" and str(p).endswith(".json")):
        return json.loads(content)
    return content


def write(path: PathLike, data: Any, format: str = "auto") -> None:
    """Write ``data`` to ``path``.

    - If ``format == 'json'`` the data is serialized as JSON.
    - If ``format == 'auto'`` and ``data`` is a ``dict`` or ``list`` the
      data is serialized as JSON.
    - Otherwise ``str(data)`` is written.
    """
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    if format == "json" or (format == "auto" and isinstance(data, (dict, list))):
        content = json.dumps(data, indent=2)
    else:
        content = str(data)
    p.write_text(content, encoding="utf-8")


def append(path: PathLike, data: Any) -> None:
    """Append ``data`` as a line to ``path`` (creates the file if missing)."""
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    # Use text mode and ensure a newline is appended
    with p.open("a", encoding="utf-8") as fh:
        fh.write(str(data) + "\n")


def exists(path: PathLike) -> bool:
    """Return True if the path exists on disk."""
    return Path(path).expanduser().exists()


def ls(path: PathLike = ".", pattern: str = "*") -> List[str]:
    """List entries in ``path`` matching ``pattern``.

    Returns a list of path strings.
    """
    return [str(p) for p in Path(path).expanduser().glob(pattern)]


def find(pattern: str, path: PathLike = ".") -> List[str]:
    """Recursively find files under ``path`` matching ``pattern``.

    Returns a list of path strings.
    """
    return [str(p) for p in Path(path).expanduser().rglob(pattern)]


def mkdir(path: PathLike) -> None:
    """Create directory ``path`` and any missing parents (idempotent)."""
    Path(path).expanduser().mkdir(parents=True, exist_ok=True)


def grep(pattern: str, path: PathLike, recursive: bool = True) -> List[Dict[str, Any]]:
    """Search textual files for ``pattern`` under ``path``.

    Returns a list of matches, each entry is a dict with keys: ``file``,
    ``line`` (1-based), and ``text`` (the line contents, stripped).

    Non-text files, permission errors and directories are skipped and an
    informational log message is emitted.
    """
    results: List[Dict[str, Any]] = []
    paths = find("*", path) if recursive else ls(path)
    for p in paths:
        try:
            content = Path(p).read_text(encoding="utf-8")
            for i, line in enumerate(content.split("\n"), 1):
                if re.search(pattern, line):
                    results.append({"file": p, "line": i, "text": line.strip()})
        except (UnicodeDecodeError, PermissionError, IsADirectoryError) as e:
            log(f"grep skipped {p}: {e}", level="WARN")
    return results


# HTTP operations
def get(url: str, timeout: int = 30, raw: bool = False, **kwargs: Any) -> Any:
    """Perform an HTTP GET.

    If ``raw`` is True the underlying ``requests.Response`` object is
    returned. Otherwise the function attempts to decode JSON and falls back
    to returning response text.
    """
    r = requests.get(url, timeout=timeout, **kwargs)
    r.raise_for_status()
    if raw:
        return r
    try:
        return r.json()
    except Exception:
        return r.text


def post(url: str, data: Any = None, timeout: int = 30, raw: bool = False, **kwargs: Any) -> Any:
    """Perform an HTTP POST with JSON-serializable ``data``.

    Behaves like :pyfunc:`get` with respect to the ``raw`` flag and return
    semantics.
    """
    r = requests.post(url, json=data, timeout=timeout, **kwargs)
    r.raise_for_status()
    if raw:
        return r
    try:
        return r.json()
    except Exception:
        return r.text


def download(url: str, path: PathLike, timeout: int = 30) -> str:
    """Download ``url`` and write bytes to ``path``. Returns the path string."""
    r = requests.get(url, timeout=timeout, stream=True)
    r.raise_for_status()
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(r.content)
    return str(p)


# Shell interop
def sh(command: str, check: bool = False) -> str:
    """Run a shell command string and return stdout (stripped).

    When ``check`` is True a non-zero exit status raises
    :class:`subprocess.CalledProcessError`.
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, command, result.stdout, result.stderr
        )
    return result.stdout.strip()


def run(args: Sequence[str], check: bool = False) -> str:
    """Run a command provided as a sequence of arguments and return stdout.

    ``args`` should be a list/tuple containing the executable and its
    arguments. When ``check`` is True a non-zero exit status raises
    :class:`subprocess.CalledProcessError`.
    """
    result = subprocess.run(
        list(args),
        shell=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, args, result.stdout, result.stderr
        )
    return result.stdout.strip()


# Utilities
def log(msg: str, level: str = "INFO") -> None:
    """Write a simple timestamped message to stderr.

    Levels: DEBUG, INFO, WARN, ERROR
    """
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    print(f"[{timestamp}] {level}: {msg}", file=sys.stderr)


def now() -> datetime:
    """Return the current timezone-aware UTC datetime.

    Returning an aware datetime helps avoid bugs related to naive
    datetimes in code that needs to interoperate with other systems.
    """
    return datetime.now(timezone.utc)
