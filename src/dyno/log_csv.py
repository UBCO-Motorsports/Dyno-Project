import csv
from pathlib import Path

from dyno.log_schema import LOG_COLUMNS
from dyno.sample import Sample


def write_log(path: Path, samples: list[Sample]) -> None:
    """Overwrite path with a header and one row per sample. UTF-8, newline \\n."""
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(LOG_COLUMNS)
        for sample in samples:
            writer.writerow(
                [
                    sample.timestamp_utc.isoformat(),
                    sample.torque_nm,
                    sample.speed_rpm,
                    sample.power_kw,
                    sample.strain,
                    sample.valve_setpoint,
                    sample.pedal_voltage_a,
                    sample.pedal_voltage_b,
                    sample.run_state,
                ]
            )
