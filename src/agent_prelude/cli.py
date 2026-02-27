#!/usr/bin/env python3
"""Console entrypoint for the agent_prelude package."""

import sys
from importlib import import_module


def main():
    # replicate the behavior of the original agent_harness but as an entrypoint
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="Execute Python code with agent_prelude loaded"
    )
    parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        help="Install by symlinking to ~/.local/bin/agh",
    )
    parser.add_argument(
        "-p",
        "--primer",
        action="store_true",
        help="Print comprehensive usage guide for LLM",
    )
    args = parser.parse_args()

    if args.install:
        src = os.path.abspath(__file__)
        dst = os.path.expanduser("~/.local/bin/agh")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            os.remove(dst)
        os.symlink(src, dst)
        print(f"Symlinked {src} to {dst}")
        sys.exit(0)

    if args.primer:
        # Load the primer text from the top-level README for brevity
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                primer_text = f.read()
        except Exception:
            primer_text = "agent_prelude — no primer available"
        print(primer_text.strip())
        sys.exit(0)

    # Import the package
    pkg = import_module("agent_prelude")

    # Read the Python code from stdin
    code = sys.stdin.read()

    # Create a namespace with all symbols from the package
    namespace = vars(pkg).copy()

    # Execute the code in the namespace
    try:
        exec(code, namespace)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
