from datetime import UTC, datetime

import pytest

from dyno.readout import OperatorSession, readout_text
from dyno.run_state import RigCommand, RunState, TestRun
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
        "run_state": "running",
    }
    values.update(overrides)
    return Sample(**values)


def test_readout_contains_torque_speed_power_and_state():
    sample = _sample()
    text = readout_text(sample)
    assert "Torque: 10.00 N·m" in text
    assert "Speed: 1000.00 rpm" in text
    assert f"Power: {sample.power_kw:.3f} kW" in text
    assert "State: running" in text


# Example command from test_run_state — not a claim about physical rig values.
_REQUESTED = RigCommand(1.2, 1.1, 40, 0.9)


def test_operator_start_before_arm_is_illegal_and_stays_idle():
    session = OperatorSession(run=TestRun(), sample=_sample(run_state="idle"))
    with pytest.raises(ValueError, match="illegal"):
        session.start()
    assert session.run.state() is RunState.IDLE


def test_operator_arm_then_start_shows_running_in_text():
    session = OperatorSession(run=TestRun(), sample=_sample(run_state="idle"))
    session.arm()
    session.start()
    assert session.run.state() is RunState.RUNNING
    assert "State: running" in session.text()


def test_operator_stop_then_command_returns_safe():
    run = TestRun(safe_valve_setpoint=0.25)
    session = OperatorSession(run=run, sample=_sample(run_state="running"))
    session.arm()
    session.start()
    session.stop()
    commanded = session.command(_REQUESTED)
    assert commanded == RigCommand(0, 0, 0, 0.25)
