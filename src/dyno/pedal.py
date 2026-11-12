"""Pedal voltage limits (#23). Only PedalLimits lives here until clamping lands."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PedalLimits:
    minimum_v: float
    maximum_v: float
