from datetime import UTC, datetime

import pytest

from dyno.operator_app import build_session, format_manual_apply_feedback
from dyno.run_state import RigCommand
from dyno.sample import Sample


def _sample(**overrides) -> Sample:
    values = {
        "timestamp_utc": datetime(2026, 10, 19, 22, 0, tzinfo=UTC),
        "torque_nm": 10,
        "speed_rpm": 1000,
        "strain": 0.001,
        "valve_setpoint": 0.2,
        "pedal_voltage_a": 0.5,
        "pedal_voltage_b": 0.5,
        "run_state": "idle",
    }
    values.update(overrides)
    return Sample(**values)


def test_import_operator_app_does_not_require_display():
    import dyno.operator_app  # noqa: F401


def test_build_session_readout_contains_torque_and_start_before_arm_raises():
    session = build_session(_sample(), safe_valve_setpoint=0.25)
    assert "Torque:" in session.text()
    with pytest.raises(ValueError, match="illegal"):
        session.start()


def test_format_manual_apply_feedback_shows_safe_status_when_command_is_safe():
    commanded = RigCommand(0, 0, 0, 0.25)
    last_applied, status = format_manual_apply_feedback(commanded, safe_valve_setpoint=0.25)
    assert "safe command" in last_applied
    assert "0.25" in last_applied
    assert status == "Not running: safe command sent"


def test_format_manual_apply_feedback_shows_commanded_values_when_running():
    commanded = RigCommand(1.5, 0.75, 0, 0.42)
    last_applied, status = format_manual_apply_feedback(commanded, safe_valve_setpoint=0.25)
    assert "1.5" in last_applied and "0.75" in last_applied and "0.42" in last_applied
    assert status == ""
