"""Disposable Git repositories prove index handling; never stage the real repo."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import random
import string
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("pre_commit", SCRIPTS / "pre-commit.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class IndexGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mavilon gate ")
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        # A scanner stand-in tests invocation/exit propagation. Real Gitleaks
        # synthetic detection is verified independently below.
        self.scanner = self.root / "scanner"
        self.scanner.write_text("#!/bin/sh\nexit 0\n")
        self.scanner.chmod(0o755)

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def stage(self, name, content="safe\n"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        self.git("add", "--", name)

    def test_initial_commit_and_spaced_path(self):
        self.stage("a file.py", "value = 1\n")
        self.assertEqual(gate.check_staged(self.root, str(self.scanner)), 0)

    def test_partially_staged_whitespace_checks_index(self):
        self.stage("a.py", "bad = 1  \n")
        (self.root / "a.py").write_text("good = 1\n")
        self.assertNotEqual(gate.check_staged(self.root, str(self.scanner)), 0)

    def test_unstaged_whitespace_does_not_fail_clean_index(self):
        self.stage("a.py", "good = 1\n")
        (self.root / "a.py").write_text("bad = 1  \n")
        self.assertEqual(gate.check_staged(self.root, str(self.scanner)), 0)

    def test_private_path_rejected_but_deletion_allowed(self):
        self.stage("backend/.env")
        self.assertNotEqual(gate.check_staged(self.root, str(self.scanner)), 0)
        self.git("commit", "-qm", "fixture")
        self.git("rm", "backend/.env")
        self.assertEqual(gate.check_staged(self.root, str(self.scanner)), 0)

    def test_ci_tree_check_rejects_committed_private_file(self):
        import check
        self.stage("backend/private.sqlite3", "no secret pattern required\n")
        self.git("commit", "-qm", "fixture")
        with self.assertRaises(RuntimeError):
            check.static(self.root)

    def test_rename_into_private_path_rejected(self):
        self.stage("public.txt")
        self.git("commit", "-qm", "fixture")
        self.git("mv", "public.txt", ".env")
        self.assertNotEqual(gate.check_staged(self.root, str(self.scanner)), 0)

    def test_missing_scanner_and_failure_do_not_pass(self):
        self.stage("a.py")
        with self.assertRaises(FileNotFoundError):
            gate.check_staged(self.root, str(self.root / "missing"))
        self.scanner.write_text("#!/bin/sh\nexit 7\n")
        self.assertEqual(gate.check_staged(self.root, str(self.scanner)), 7)

    def test_scanner_version_must_match_pin(self):
        import check
        with patch.object(check.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout="0.0.0\n")):
            with self.assertRaises(RuntimeError):
                check.scanner()

    def test_real_scanner_reads_staged_secret_not_worktree(self):
        import check
        executable = check.scanner()  # Missing tool is a test failure, not skip.
        # Synthetic recognizable token, assembled to avoid embedding a complete
        # secret-shaped literal in repository source; never usable credentials.
        synthetic = "ghp_" + "".join(random.Random(23).choices(string.ascii_letters + string.digits, k=36))
        self.stage("fixture.txt", "token=" + synthetic + "\n")
        (self.root / "fixture.txt").write_text("removed in worktree\n")
        result = subprocess.run([executable, "git", "--pre-commit", "--staged", "--redact", "--no-banner"],
                                cwd=self.root, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(synthetic.encode(), result.stdout + result.stderr)
