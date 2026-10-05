#!/usr/bin/env python3
"""Non-mutating checks. Run from any directory; failures are never suppressed."""
import argparse
import ast
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
# Temporary CI partition only. Remove on ROADMAP APP-01/APP-02 remediation.
# The default backend/all commands always run the complete suite.
KNOWN_APPLICATION_DEFECTS = (
    "backend/tests/test_users_contract.py::test_returning_session_matches_actual_frontend_request",
    "backend/tests/test_users_contract.py::test_populated_profile_matches_persisted_and_frontend_shape",
)


def private_path(name):
    path = PurePosixPath(name)
    base = path.name.lower()
    if name in (".env.local.example", "backend/.env.example"):
        return False
    return (base == ".env" or base.startswith(".env.")
            or base.endswith((".pem", ".key", ".db", ".sqlite", ".sqlite3", ".zip", ".log"))
            or ".db-" in base or ".sqlite-" in base or ".sqlite3-" in base
            or bool(set(path.parts) & {"node_modules", ".next", ".venv", "venv", ".tools", ".hf-cache", "__pycache__", ".aws", "private"}))


def run(args, **kwargs):
    print("+ " + " ".join(map(str, args)), flush=True)
    return subprocess.run(args, cwd=ROOT, check=False, **kwargs).returncode


def python():
    candidate = ROOT / "backend/.venv/bin/python"
    return str(candidate) if candidate.exists() else sys.executable


def scanner():
    candidate = ROOT / ".tools/gitleaks"
    executable = str(candidate) if candidate.exists() else "gitleaks"
    expected = json.loads((ROOT / "scripts/gitleaks.json").read_text())["version"]
    result = subprocess.run([executable, "version"], capture_output=True, text=True, check=True)
    if result.stdout.strip().removeprefix("v") != expected:
        raise RuntimeError(f"Gitleaks {expected} required; run python3 scripts/install-gitleaks.py")
    return executable


def static(root=ROOT):
    result = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                            cwd=root, capture_output=True, check=True)
    count = 0
    for raw in set(result.stdout.split(b"\0")) - {b""}:
        name = os.fsdecode(raw)
        path = root / name
        if not path.is_file():
            continue
        if private_path(name):
            raise RuntimeError(f"Private/generated path in source tree: {name!r}")
        if path.suffix == ".py":
            ast.parse(path.read_bytes(), filename=str(path))
            count += 1
        elif path.suffix == ".json":
            json.loads(path.read_text())
            count += 1
    print(f"Parsed {count} Python/JSON files; no application imports.")
    manifest_path = root / "package.json"
    lock_path = root / "package-lock.json"
    if manifest_path.exists() and lock_path.exists():
        manifest = json.loads(manifest_path.read_text())
        locked = json.loads(lock_path.read_text())["packages"][""]
        for key in ("dependencies", "devDependencies", "engines"):
            if manifest.get(key, {}) != locked.get(key, {}):
                raise RuntimeError(f"Manifest/lock root mismatch: {key}")
    return 0


def check(name):
    if name == "static":
        return static()
    if name in ("backend", "backend-foundation", "known-application-defects"):
        command = [python(), "-m", "pytest", "-c", "backend/pytest.ini"]
        if name == "known-application-defects":
            print("Known application defects: ROADMAP APP-01 and APP-02; failures remain visible.", flush=True)
            command.extend(KNOWN_APPLICATION_DEFECTS)
        else:
            command.append("backend/tests")
            if name == "backend-foundation":
                # pytest reports node IDs relative to its backend/ rootdir.
                command.extend(f"--deselect={test.removeprefix('backend/')}" for test in KNOWN_APPLICATION_DEFECTS)
        return run(command)
    if name == "frontend":
        results = [run(["npm", "run", task]) for task in ("lint", "typecheck", "build")]
        return int(any(results))
    if name == "gates":
        return run([sys.executable, "-m", "unittest", "discover", "-s", "scripts/tests", "-v"])
    if name == "audit-npm":
        return run(["npm", "audit", "--audit-level=high"])
    if name == "audit-python":
        # Audit the installed resolution, including transitive dependencies.
        return run([python(), "-m", "pip_audit"])
    if name == "secrets":
        executable = scanner()
        history = run([executable, "git", "--redact", "--no-banner", str(ROOT)])
        # Include newly authored/unstaged source without scanning ignored private
        # environments, databases, caches or downloaded dependencies.
        names = subprocess.check_output(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT)
        with tempfile.TemporaryDirectory(prefix="mavilon-scan-") as temporary:
            for raw in set(names.split(b"\0")) - {b""}:
                path = Path(os.fsdecode(raw))
                source = ROOT / path
                if source.is_symlink():
                    raise RuntimeError(f"Review symlink before scanning: {path}")
                if source.is_file():
                    destination = Path(temporary) / path
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())
            current = run([executable, "dir", "--redact", "--no-banner", temporary])
        return int(bool(history or current))
    if name == "all":
        results = [check(task) for task in ("static", "gates", "backend", "frontend")]
        return int(any(results))
    raise ValueError(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=["static", "backend", "backend-foundation",
                                           "known-application-defects", "frontend", "gates", "all",
                                           "audit-npm", "audit-python", "secrets"])
    args = parser.parse_args()
    try:
        sys.exit(check(args.check))
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, SyntaxError) as exc:
        print(f"Check failed: {exc}", file=sys.stderr)
        sys.exit(1)
