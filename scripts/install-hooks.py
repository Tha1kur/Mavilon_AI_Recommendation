#!/usr/bin/env python3
"""Activate this clone's hook only when no existing hook setup is displaced."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


if __name__ == "__main__":
    configured = git("config", "--show-origin", "--get", "core.hooksPath")
    if configured.returncode not in (0, 1):
        sys.exit(configured.stderr)
    if configured.returncode == 0:
        value = git("config", "--get", "core.hooksPath").stdout.strip()
        if value == ".githooks":
            print("Repository hooks already configured.")
            sys.exit(0)
        sys.exit("Existing hooksPath preserved; reconcile it manually: " + configured.stdout.strip())
    hooks_path = git("rev-parse", "--git-path", "hooks")
    if hooks_path.returncode:
        sys.exit(hooks_path.stderr)
    hooks = ROOT / hooks_path.stdout.strip()
    active = [p.name for p in hooks.iterdir() if p.is_file() and not p.name.endswith(".sample")] if hooks.exists() else []
    if active:
        sys.exit("Existing hook files preserved; reconcile manually: " + ", ".join(active))
    result = git("config", "--local", "core.hooksPath", ".githooks")
    if result.returncode:
        sys.exit(result.stderr)
    print("Activated .githooks in this clone. Restore prior unset state with: git config --local --unset core.hooksPath")
