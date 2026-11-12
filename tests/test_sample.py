import math
from datetime import UTC, datetime

import pytest

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


def test_power_comes_from_torque_and_speed():
    expected = 10 * 1000 * 2 * math.pi / 60_000
    assert _sample().power_kw == pytest.approx(expected)


def test_sample_is_immutable():
    sample = _sample()
    with pytest.raises(AttributeError):
        sample.torque_nm = 99  # type: ignore[misc]


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone"):
        _sample(timestamp_utc=datetime(2026, 10, 19, 22, 0))
