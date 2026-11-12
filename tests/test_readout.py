from datetime import UTC, datetime

from dyno.readout import readout_text
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
