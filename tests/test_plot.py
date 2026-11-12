from datetime import UTC, datetime

import pytest

from dyno.log_csv import write_log
from dyno.plot import plot_run
from dyno.sample import Sample


def _sample(speed_rpm: float, torque_nm: float) -> Sample:
    return Sample(
        timestamp_utc=datetime(2026, 11, 19, tzinfo=UTC),
        torque_nm=torque_nm,
        speed_rpm=speed_rpm,
        strain=0.0,
        valve_setpoint=0.3,
        pedal_voltage_a=1.5,
        pedal_voltage_b=0.75,
        run_state="running",
    )


def test_plot_writes_a_png(tmp_path):
    csv_path = tmp_path / "run.csv"
    write_log(csv_path, [_sample(1000, 10), _sample(2000, 12), _sample(3000, 11)])
    png_path = tmp_path / "run.png"
    plot_run(csv_path, png_path)
    assert png_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_empty_log_is_rejected(tmp_path):
    csv_path = tmp_path / "empty.csv"
    write_log(csv_path, [])
    with pytest.raises(ValueError, match="no samples"):
        plot_run(csv_path, tmp_path / "empty.png")
