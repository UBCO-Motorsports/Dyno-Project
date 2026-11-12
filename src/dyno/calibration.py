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


def apply_calibration(raw: float, gain: float, offset: float) -> float:
    """engineering = gain * raw + offset."""
    if not (math.isfinite(raw) and math.isfinite(gain) and math.isfinite(offset)):
        raise ValueError("raw, gain, and offset must be finite numbers")
    return gain * raw + offset


def calibration_residuals(
    raw_points: list[float],
    reference_points: list[float],
    gain: float,
    offset: float,
) -> list[float]:
    """reference - apply_calibration(raw, gain, offset), for each point, in order."""
    return [
        ref - apply_calibration(raw, gain, offset)
        for raw, ref in zip(raw_points, reference_points, strict=True)
    ]


def maximum_abs_residual(residuals: list[float]) -> float:
    """Largest absolute residual. This is the error figure stored with a calibration.

    The value is the maximum absolute residual over the calibration points, not
    a full laboratory uncertainty budget.
    """
    if not residuals:
        raise ValueError("residuals must not be empty")
    if not all(math.isfinite(value) for value in residuals):
        raise ValueError("all residuals must be finite numbers")
    return max(abs(value) for value in residuals)
