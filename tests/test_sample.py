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
    # 10 N·m at 1000 rpm ≈ 1.0471975512 kW (hand-computed)
    assert _sample().power_kw == pytest.approx(1.0471975512)


def test_power_is_not_a_constructor_argument():
    with pytest.raises(TypeError):
        _sample(power_kw=1.0)


def test_sample_is_immutable():
    sample = _sample()
    with pytest.raises(AttributeError):
        sample.torque_nm = 99  # type: ignore[misc]


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone"):
        _sample(timestamp_utc=datetime(2026, 10, 19, 22, 0))
