#!/usr/bin/env python3
"""Append a chronicle entry to today's chronicle file.

Usage:
  ./scripts/append_chronicle.py --title "Short title" --summary "One-line summary" \
      [--participants "assistant,user"] [--commands "cmd1; cmd2"] [--files file1 file2]

If --files is omitted, the script will try to infer changed files via `git status --porcelain`.
The chronicle file used is chronicles/YYYY-MM-DD-session.md (created if missing).
"""
import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import shlex
import sys


def git_changed_files():
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], text=True)
    except Exception:
        return []
    files = []
    for line in out.splitlines():
        if not line:
            continue
        # format: XY <path>
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            files.append(parts[1])
    return files


def append_entry(title, summary, participants, commands, files):
    today = datetime.utcnow().date().isoformat()
    chronicle_dir = Path("chronicles")
    chronicle_dir.mkdir(parents=True, exist_ok=True)
    path = chronicle_dir / f"{today}-session.md"

    timestamp = datetime.utcnow().isoformat() + "Z"

    lines = []
    lines.append(f"## {timestamp} — {title}\n")
    lines.append(f"Participants: {participants}\n")
    lines.append("\n")
    lines.append("Summary\n")
    lines.append("- " + summary + "\n")
    lines.append("\n")
    if commands:
        lines.append("Commands run (representative)\n")
        for c in commands:
            lines.append(f"- `{c}`\n")
        lines.append("\n")
    if files:
        lines.append("Files added/modified\n")
        for f in files:
            lines.append(f"- {f}\n")
        lines.append("\n")
    lines.append("Suggested next steps\n")
    lines.append("- (add items here)\n")
    lines.append("\n---\n\n")

    # Prepend to file: keep latest entries at top
    if path.exists():
        existing = path.read_text(encoding="utf-8")
    else:
        # Create a header for the chronicle if missing
        existing = f"# Chronicle — {today}\n\n"

    new_content = existing + "".join(lines)
    path.write_text(new_content, encoding="utf-8")
    print(f"Appended chronicle to {path}")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--participants", default="assistant,user")
    p.add_argument("--commands", default="", help="Semicolon-separated commands")
    p.add_argument("--files", nargs="*", help="List of files to record (optional)")
    args = p.parse_args(argv)

    files = args.files or git_changed_files()
    commands = [c.strip() for c in args.commands.split(";") if c.strip()]

    append_entry(args.title, args.summary, args.participants, commands, files)


if __name__ == "__main__":
    main()
