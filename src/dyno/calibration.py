import math


def apply_calibration(raw: float, gain: float, offset: float) -> float:
    """engineering = gain * raw + offset."""
    if not (math.isfinite(raw) and math.isfinite(gain) and math.isfinite(offset)):
        raise ValueError("raw, gain, and offset must be finite numbers")
    return gain * raw + offset
