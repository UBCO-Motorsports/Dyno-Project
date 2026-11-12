import csv
from datetime import UTC, datetime

from dyno.log_csv import write_log
from dyno.log_schema import LOG_COLUMNS
from dyno.sample import Sample


def test_write_log_has_the_fixed_header_and_one_row(tmp_path):
    sample = Sample(
        timestamp_utc=datetime(2026, 10, 19, 22, 0, tzinfo=UTC),
        torque_nm=10,
        speed_rpm=1000,
        strain=0.001,
        valve_setpoint=0.2,
        pedal_voltage_a=0.5,
        pedal_voltage_b=0.4,
        run_state="running",
    )
    path = tmp_path / "run.csv"
    write_log(path, [sample])
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    assert lines[0] == ",".join(LOG_COLUMNS)
    assert "2026-10-19T22:00:00+00:00" in lines[1]
    assert "running" in lines[1]
    assert "\r\n" not in text


def test_empty_run_still_writes_the_header(tmp_path):
    path = tmp_path / "empty.csv"
    write_log(path, [])
    assert path.read_text(encoding="utf-8").split("\n")[0] == ",".join(LOG_COLUMNS)


def test_values_line_up_with_their_headers(tmp_path):
    sample = Sample(
        timestamp_utc=datetime(2026, 10, 19, 22, 0, tzinfo=UTC),
        torque_nm=10,
        speed_rpm=1000,
        strain=0.001,
        valve_setpoint=0.2,
        pedal_voltage_a=0.5,
        pedal_voltage_b=0.4,
        run_state="running",
    )
    path = tmp_path / "run.csv"
    write_log(path, [sample])
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    row = rows[0]
    assert row["torque_nm"] == "10"
    assert row["speed_rpm"] == "1000"
    assert row["pedal_voltage_b"] == "0.4"
    assert row["valve_setpoint"] == "0.2"
    assert row["run_state"] == "running"
    assert row["timestamp_utc"] == "2026-10-19T22:00:00+00:00"
