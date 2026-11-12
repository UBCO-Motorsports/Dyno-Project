from typing import Protocol


class ForceSource(Protocol):
    def force_n(self) -> float: ...


class StrainSource(Protocol):
    def raw(self) -> float: ...


class SpeedSource(Protocol):
    def speed_rpm(self) -> float: ...


class Valve(Protocol):
    def set_setpoint(self, setpoint: float) -> None: ...

    def position(self) -> float: ...


class PedalOutput(Protocol):
    def set_voltages(self, channel_a: float, channel_b: float) -> None: ...

    def voltages(self) -> tuple[float, float]: ...
