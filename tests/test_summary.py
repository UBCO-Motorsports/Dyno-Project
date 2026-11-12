from datetime import UTC, datetime

import pytest

from dyno.sample import Sample
from dyno.summary import summarise


def _sample(torque: float, speed: float) -> Sample:
    return Sample(
        timestamp_utc=datetime(2026, 10, 19, 22, 0, tzinfo=UTC),
        torque_nm=torque,
        speed_rpm=speed,
        strain=0,
        valve_setpoint=0,
        pedal_voltage_a=0,
        pedal_voltage_b=0,
        run_state="running",
    )


def test_min_max_and_mean():
    summary = summarise([_sample(10, 1000), _sample(30, 3000)])
    assert summary.torque_nm.minimum == 10
    assert summary.torque_nm.maximum == 30
    assert summary.torque_nm.mean == 20
    assert summary.speed_rpm.mean == 2000
    assert summary.power_kw.minimum == pytest.approx(_sample(10, 1000).power_kw)
    assert summary.power_kw.maximum == pytest.approx(_sample(30, 3000).power_kw)


def test_empty_log_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        summarise([])
