import csv
import math
from datetime import datetime
from pathlib import Path

from dyno.log_schema import LOG_COLUMNS
from dyno.power import mechanical_power_kw
from dyno.sample import Sample


def _sample_cell(sample: Sample, column: str):
    if column == "timestamp_utc":
        return sample.timestamp_utc.isoformat()
    return getattr(sample, column)


def write_log(path: Path, samples: list[Sample]) -> None:
    """Overwrite path with a header and one row per sample. UTF-8, newline \\n."""
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(LOG_COLUMNS)
        for sample in samples:
            writer.writerow([_sample_cell(sample, column) for column in LOG_COLUMNS])


def read_log(path: Path) -> list[Sample]:
    """Read a file produced by write_log. Power is recomputed, not trusted from the file."""
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("log file is empty") from None
        if tuple(reader.fieldnames) != LOG_COLUMNS:
            raise ValueError("unexpected log header")
        samples: list[Sample] = []
        for row in reader:
            if not row or not any(row.values()):
                continue
            timestamp_utc = datetime.fromisoformat(row["timestamp_utc"])
            torque_nm = float(row["torque_nm"])
            speed_rpm = float(row["speed_rpm"])
            stored_power_kw = float(row["power_kw"])
            expected_power_kw = mechanical_power_kw(torque_nm, speed_rpm)
            if not math.isclose(stored_power_kw, expected_power_kw, rel_tol=1e-6):
                raise ValueError("stored power_kw does not match mechanical_power_kw")
            samples.append(
                Sample(
                    timestamp_utc=timestamp_utc,
                    torque_nm=torque_nm,
                    speed_rpm=speed_rpm,
                    strain=float(row["strain"]),
                    valve_setpoint=float(row["valve_setpoint"]),
                    pedal_voltage_a=float(row["pedal_voltage_a"]),
                    pedal_voltage_b=float(row["pedal_voltage_b"]),
                    run_state=row["run_state"],
                )
            )
        return samples
