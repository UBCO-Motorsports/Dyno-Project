from datetime import UTC, datetime

import pytest

from dyno.operator_app import build_session
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
