"""Agreed operating envelope for the dyno motor.

Confirmed in the proposal notes. Change these only with sign-off from
Mechanical and Electrical, and record who confirmed the change.
"""

PEAK_TORQUE_NM = 150.0
MAX_SPEED_RPM = 7000.0
POWER_CAP_KW = 80.0
MIN_STRAIN_SAMPLE_HZ = 10.0


def exceeds_power_cap(power_kw: float) -> bool:
    """True when power_kw is at or above POWER_CAP_KW. The cap is "below 80 kW"."""
    return power_kw >= POWER_CAP_KW