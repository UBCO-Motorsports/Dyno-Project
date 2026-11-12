import math
import statistics


def fit_calibration_line(
    raw_points: list[float], reference_points: list[float]
) -> tuple[float, float]:
    """Least-squares (gain, offset) for reference = gain * raw + offset. Needs three or more points."""
    if len(raw_points) < 3:
        raise ValueError("need at least three points")
    if len(raw_points) != len(reference_points):
        raise ValueError("raw and reference lists must be the same length")
    if len(set(raw_points)) < len(raw_points):
        raise ValueError("raw values must be distinct")
    if not all(math.isfinite(x) for x in raw_points) or not all(
        math.isfinite(x) for x in reference_points
    ):
        raise ValueError("all points must be finite numbers")

    try:
        gain, offset = statistics.linear_regression(raw_points, reference_points)
    except statistics.StatisticsError as exc:
        raise ValueError("raw values must be distinct") from exc

    return gain, offset
