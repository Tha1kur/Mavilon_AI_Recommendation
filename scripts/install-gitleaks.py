#!/usr/bin/env python3
"""Download a pinned upstream binary, verify its checked-in SHA256, install locally."""
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    config = json.loads((ROOT / "scripts/gitleaks.json").read_text())
    system = {"Darwin": "darwin", "Linux": "linux"}.get(platform.system())
    arch = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x64", "AMD64": "x64"}.get(platform.machine())
    asset = f"gitleaks_{config['version']}_{system}_{arch}.tar.gz"
    if asset not in config["sha256"]:
        raise SystemExit("Unsupported platform; use a supported macOS/Linux machine or review an upstream binary manually.")
    url = f"https://github.com/gitleaks/gitleaks/releases/download/v{config['version']}/{asset}"
    with urllib.request.urlopen(url, timeout=60) as response:
        archive = response.read()
    if hashlib.sha256(archive).hexdigest() != config["sha256"][asset]:
        raise SystemExit("Checksum mismatch; nothing installed.")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
        member = bundle.getmember("gitleaks")
        if not member.isfile():
            raise SystemExit("Expected a regular binary in release archive.")
        binary = bundle.extractfile(member).read()
    destination = ROOT / ".tools/gitleaks"
    destination.parent.mkdir(exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    temporary.write_bytes(binary)
    temporary.chmod(0o755)
    version = subprocess.check_output([str(temporary), "version"], text=True).strip()
    if version.removeprefix("v") != config["version"]:
        temporary.unlink()
        raise SystemExit("Downloaded binary reported unexpected version.")
    temporary.replace(destination)
    print(f"Installed verified Gitleaks {version} at {destination}")


if __name__ == "__main__":
    main()
