import ast
from pathlib import Path

import pytest

from dyno.run_state import RigCommand
from dyno.watchdog import command_for_heartbeat, heartbeat_expired

# Example timestamps and timeout from issue #29.
_LAST_SEEN_S = 10.0
_TIMEOUT_S = 0.5

_REQUESTED = RigCommand(1.2, 1.1, 40, 0.9)


def test_heartbeat_not_expired_inside_timeout():
    assert heartbeat_expired(_LAST_SEEN_S, 10.4, _TIMEOUT_S) is False


def test_heartbeat_expired_beyond_timeout():
    assert heartbeat_expired(_LAST_SEEN_S, 10.6, _TIMEOUT_S) is True


def test_command_returns_requested_when_heartbeat_fresh():
    result = command_for_heartbeat(
        _LAST_SEEN_S,
        10.4,
        _TIMEOUT_S,
        _REQUESTED,
        safe_valve_setpoint=0.0,
    )
    assert result == _REQUESTED


def test_command_returns_safe_when_heartbeat_expired():
    safe_valve_setpoint = 0.0
    result = command_for_heartbeat(
        _LAST_SEEN_S,
        10.6,
        _TIMEOUT_S,
        _REQUESTED,
        safe_valve_setpoint=safe_valve_setpoint,
    )
    assert result == RigCommand(0, 0, 0, safe_valve_setpoint)


def test_zero_timeout_raises():
    with pytest.raises(ValueError, match="timeout"):
        heartbeat_expired(_LAST_SEEN_S, 10.4, 0)


def test_backwards_clock_raises():
    with pytest.raises(ValueError, match="clock"):
        heartbeat_expired(_LAST_SEEN_S, 9.9, _TIMEOUT_S)


def test_watchdog_module_has_no_time_or_socket_imports():
    module_path = Path(__file__).resolve().parents[1] / "src" / "dyno" / "watchdog.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    banned = {"time", "socket"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in banned, f"banned import {alias.name}"
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            assert root not in banned, f"banned import from {node.module}"
