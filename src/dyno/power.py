"""Mechanical power from measured torque and shaft speed."""

import math


def mechanical_power_kw(torque_nm: float, speed_rpm: float) -> float:
    """P (kW) = T (N·m) * speed (rpm) * 2π / 60_000."""
    if not (math.isfinite(torque_nm) and math.isfinite(speed_rpm)):
        raise ValueError("torque and speed must be finite numbers")
    if speed_rpm < 0:
        raise ValueError("speed must not be negative")
    return torque_nm * speed_rpm * 2 * math.pi / 60_000
