import csv
from pathlib import Path

from dyno.log_schema import LOG_COLUMNS
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
