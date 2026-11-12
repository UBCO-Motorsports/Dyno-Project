import csv
from datetime import UTC, datetime

import pytest

from dyno.log_csv import read_log, write_log
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


def test_round_trip(tmp_path):
    original = [
        Sample(
            timestamp_utc=datetime(2026, 10, 19, 22, 0, tzinfo=UTC),
            torque_nm=10,
            speed_rpm=1000,
            strain=0.001,
            valve_setpoint=0.2,
            pedal_voltage_a=0.5,
            pedal_voltage_b=0.4,
            run_state="running",
        )
    ]
    path = tmp_path / "run.csv"
    write_log(path, original)
    loaded = read_log(path)
    assert loaded == original


def test_loaded_power_matches_the_formula(tmp_path):
    original = Sample(
        timestamp_utc=datetime(2026, 10, 19, 22, 0, tzinfo=UTC),
        torque_nm=10,
        speed_rpm=1000,
        strain=0.0,
        valve_setpoint=0.0,
        pedal_voltage_a=0.0,
        pedal_voltage_b=0.0,
        run_state="running",
    )
    path = tmp_path / "run.csv"
    write_log(path, [original])
    # 10 N·m at 1000 rpm ≈ 1.0471975511965976 kW (README); property must match after read
    assert read_log(path)[0].power_kw == 1.0471975511965976
    assert read_log(path)[0].power_kw == original.power_kw


def test_tampered_power_cell_raises(tmp_path):
    sample = Sample(
        timestamp_utc=datetime(2026, 10, 19, 22, 0, tzinfo=UTC),
        torque_nm=10,
        speed_rpm=1000,
        strain=0.0,
        valve_setpoint=0.0,
        pedal_voltage_a=0.0,
        pedal_voltage_b=0.0,
        run_state="running",
    )
    path = tmp_path / "run.csv"
    write_log(path, [sample])
    lines = path.read_text(encoding="utf-8").split("\n")
    fields = lines[1].split(",")
    power_idx = LOG_COLUMNS.index("power_kw")
    fields[power_idx] = "0"
    lines[1] = ",".join(fields)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="power"):
        read_log(path)
