"""Pedal voltage bounds and released-pedal command."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PedalLimits:
    minimum_v: float
    maximum_v: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.minimum_v) and math.isfinite(self.maximum_v)):
            raise ValueError("limits must be finite numbers")
        if self.minimum_v > self.maximum_v:
            raise ValueError("limits: minimum_v must not exceed maximum_v")


def clamp_pedal(voltage: float, limits: PedalLimits) -> float:
    """Clamp into [minimum_v, maximum_v]."""
    return max(limits.minimum_v, min(limits.maximum_v, voltage))


def stopped_pedal() -> tuple[float, float]:
    """Released pedal. Both channels are 0."""
    return (0.0, 0.0)


def pedal_voltages(position: float, a: PedalLimits, b: PedalLimits) -> tuple[float, float]:
    """position is 0.0 (released) to 1.0 (full). Each channel is linear across its own range."""
    if not (0.0 <= position <= 1.0):
        raise ValueError("position must be between 0.0 and 1.0")
    span_a = a.maximum_v - a.minimum_v
    span_b = b.maximum_v - b.minimum_v
    voltage_a = a.minimum_v + position * span_a
    voltage_b = b.minimum_v + position * span_b
    return (voltage_a, voltage_b)


def pedals_agree(
    voltage_a: float,
    voltage_b: float,
    a: PedalLimits,
    b: PedalLimits,
    threshold: float = 0.10,
) -> bool:
    """True when the two channels imply positions within `threshold` of each other."""
    span_a = a.maximum_v - a.minimum_v
    span_b = b.maximum_v - b.minimum_v
    position_a = (voltage_a - a.minimum_v) / span_a
    position_b = (voltage_b - b.minimum_v) / span_b
    return abs(position_a - position_b) <= threshold
