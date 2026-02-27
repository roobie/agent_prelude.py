"""agent_prelude package

This module provides the same helper functions as the top-level agent_prelude.py
but packaged so the project is installable.
"""

import sys
import re
import json
from pathlib import Path
from datetime import datetime
import subprocess
import requests


# Filesystem operations
def read(path, format="auto"):
    """Read file, auto-detecting JSON/text."""
    content = Path(path).expanduser().read_text(encoding="utf-8")
    if format == "json" or (format == "auto" and path.endswith(".json")):
        return json.loads(content)
    return content


def write(path, data, format="auto"):
    """Write file, auto-serializing dicts to JSON."""
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json" or (format == "auto" and isinstance(data, (dict, list))):
        content = json.dumps(data, indent=2)
    else:
        content = str(data)
    path.write_text(content, encoding="utf-8")


def append(path, data):
    """Append to file."""
    Path(path).expanduser().touch()
    with open(Path(path).expanduser(), "a") as f:
        f.write(str(data) + "\n")


def exists(path):
    """Check if path exists."""
    return Path(path).expanduser().exists()


def ls(path=".", pattern="*"):
    """List files matching pattern."""
    return [str(p) for p in Path(path).expanduser().glob(pattern)]


def find(pattern, path="."):
    """Recursively find files matching pattern."""
    return [str(p) for p in Path(path).expanduser().rglob(pattern)]


def mkdir(path):
    """Create directory (and parents)."""
    Path(path).expanduser().mkdir(parents=True, exist_ok=True)


def grep(pattern, path, recursive=True):
    """Search for pattern in files."""
    results = []
    paths = find("*", path) if recursive else ls(path)
    for p in paths:
        try:
            content = Path(p).read_text()
            for i, line in enumerate(content.split("\n"), 1):
                if re.search(pattern, line):
                    results.append({"file": p, "line": i, "text": line.strip()})
        except (UnicodeDecodeError, PermissionError, IsADirectoryError) as e:
            log(f"grep skipped {p}: {e}", level="WARN")
    return results


# HTTP operations
def get(url, timeout=30, raw=False, **kwargs):
    """HTTP GET, returns JSON if possible, else text."""
    r = requests.get(url, timeout=timeout, **kwargs)
    r.raise_for_status()
    if raw:
        return r
    try:
        return r.json()
    except Exception:
        return r.text


def post(url, data=None, timeout=30, raw=False, **kwargs):
    """HTTP POST with JSON data."""
    r = requests.post(url, json=data, timeout=timeout, **kwargs)
    r.raise_for_status()
    if raw:
        return r
    try:
        return r.json()
    except Exception:
        return r.text


def download(url, path, timeout=30):
    """Download file from URL."""
    r = requests.get(url, timeout=timeout, stream=True)
    r.raise_for_status()
    Path(path).expanduser().write_bytes(r.content)
    return path


# Shell interop
def sh(command, check=False):
    """Run shell command, return stdout."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, command, result.stdout, result.stderr
        )
    return result.stdout.strip()


def run(args, check=False):
    """Run command with args list, return stdout."""
    result = subprocess.run(
        args,
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
def log(msg, level="INFO"):
    """Simple logging to stderr. Levels: DEBUG, INFO, WARN, ERROR."""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {level}: {msg}", file=sys.stderr)


def now():
    """Current datetime."""
    return datetime.now()
