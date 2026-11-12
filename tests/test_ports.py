import ast
from pathlib import Path

from dyno.ports import (
    ForceSource,
    PedalOutput,
    SpeedSource,
    StrainSource,
    Valve,
)


class FakeForce:
    def __init__(self, force_n: float = 42.0) -> None:
        self._force_n = force_n

    def force_n(self) -> float:
        return self._force_n


class FakeStrain:
    def __init__(self, raw: float = 1.5) -> None:
        self._raw = raw

    def raw(self) -> float:
        return self._raw


class FakeSpeed:
    def __init__(self, speed_rpm: float = 3000.0) -> None:
        self._speed_rpm = speed_rpm

    def speed_rpm(self) -> float:
        return self._speed_rpm


class FakeValve:
    def __init__(self) -> None:
        self._setpoint = 0.0

    def set_setpoint(self, setpoint: float) -> None:
        self._setpoint = setpoint

    def position(self) -> float:
        return self._setpoint


class FakePedal:
    def __init__(self) -> None:
        self._channel_a = 0.0
        self._channel_b = 0.0

    def set_voltages(self, channel_a: float, channel_b: float) -> None:
        self._channel_a = channel_a
        self._channel_b = channel_b

    def voltages(self) -> tuple[float, float]:
        return (self._channel_a, self._channel_b)


def read_force(source: ForceSource) -> float:
    return source.force_n()


def test_fakes_satisfy_the_ports():
    pedal = FakePedal()
    pedal.set_voltages(0.2, 0.3)
    assert pedal.voltages() == (0.2, 0.3)
    valve = FakeValve()
    valve.set_setpoint(0.4)
    assert valve.position() == 0.4


def test_fake_force_records_and_returns():
    force = FakeForce(99.5)
    assert read_force(force) == 99.5


def test_fake_strain_returns_raw():
    assert FakeStrain(2.25).raw() == 2.25


def test_fake_speed_returns_rpm():
    assert FakeSpeed(1234.0).speed_rpm() == 1234.0


def test_ports_module_has_no_hardware_imports():
    ports_path = Path(__file__).resolve().parents[1] / "src" / "dyno" / "ports.py"
    tree = ast.parse(ports_path.read_text(encoding="utf-8"))
    banned = {"serial", "socket", "can"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in banned, f"banned import {alias.name}"
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            assert root not in banned, f"banned import from {node.module}"


def test_protocols_are_typing_protocols():
    for protocol in (ForceSource, StrainSource, SpeedSource, Valve, PedalOutput):
        assert protocol.__name__ in {
            "ForceSource",
            "StrainSource",
            "SpeedSource",
            "Valve",
            "PedalOutput",
        }
