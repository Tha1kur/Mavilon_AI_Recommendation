#!/usr/bin/env python3
"""Inspect the index, not unstaged content. No installs or source mutations."""
import os
import subprocess
import sys

from check import private_path, scanner


def check_staged(root, executable):
    names = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT",
                            "--no-renames", "-z"], cwd=root, capture_output=True, check=True).stdout
    blocked = [os.fsdecode(p) for p in names.split(b"\0") if p and private_path(os.fsdecode(p))]
    if blocked:
        print("Private/generated paths staged: " + ", ".join(repr(p) for p in blocked), file=sys.stderr)
        return 1
    whitespace = subprocess.run(["git", "diff", "--cached", "--check"], cwd=root)
    if whitespace.returncode:
        return whitespace.returncode
    return subprocess.run([executable, "git", "--pre-commit", "--staged", "--redact", "--no-banner"],
                          cwd=root).returncode


if __name__ == "__main__":
    try:
        root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                              text=True, check=True).stdout.strip()
        sys.exit(check_staged(root, scanner()))
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Pre-commit failed: {exc}. See README hook setup.", file=sys.stderr)
        sys.exit(1)
