"""Guard ordinary tests against network access and model downloads."""
import os
import socket

import pytest

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"


_network_guard = pytest.MonkeyPatch()


def pytest_sessionstart(session):
    # Apply before collection, so future import-time network calls fail too.
    def denied(*args, **kwargs):
        raise AssertionError("Network access is forbidden in deterministic tests")
    for name in ("connect", "connect_ex", "sendto"):
        _network_guard.setattr(socket.socket, name, denied)
    _network_guard.setattr(socket, "create_connection", denied)
    _network_guard.setattr(socket, "getaddrinfo", denied)


def pytest_sessionfinish(session, exitstatus):
    _network_guard.undo()
