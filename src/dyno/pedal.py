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
