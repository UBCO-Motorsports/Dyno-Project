"""Load and validate rig.toml settings."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from dyno.pedal import PedalLimits

_TOP_LEVEL_KEYS = frozenset(
    {
        "arm_length_m",
        "pedal_released_v",
        "safe_valve_setpoint",
        "heartbeat_timeout_s",
        "pedal_a",
        "pedal_b",
    }
)
_PEDAL_TABLE_KEYS = frozenset({"minimum_v", "maximum_v"})


@dataclass(frozen=True)
class RigConfig:
    arm_length_m: float
    pedal_a: PedalLimits
    pedal_b: PedalLimits
    pedal_released_v: float
    safe_valve_setpoint: float
    heartbeat_timeout_s: float


def load_rig_config(path: Path) -> RigConfig:
    """Read and check a rig.toml file. Raise ValueError naming the bad key."""
    data = tomllib.loads(path.read_text(encoding="utf-8"))

    for key in data:
        if key not in _TOP_LEVEL_KEYS:
            raise ValueError(key)

    for key in _TOP_LEVEL_KEYS:
        if key not in data:
            raise ValueError(key)

    pedal_a = _read_pedal_table("pedal_a", data["pedal_a"])
    pedal_b = _read_pedal_table("pedal_b", data["pedal_b"])

    arm_length_m = _require_float("arm_length_m", data["arm_length_m"])
    if arm_length_m <= 0:
        raise ValueError("arm_length_m")

    heartbeat_timeout_s = _require_float("heartbeat_timeout_s", data["heartbeat_timeout_s"])
    if heartbeat_timeout_s <= 0:
        raise ValueError("heartbeat_timeout_s")

    pedal_released_v = _require_float("pedal_released_v", data["pedal_released_v"])
    if pedal_released_v < pedal_a.minimum_v or pedal_released_v > pedal_a.maximum_v:
        raise ValueError("pedal_released_v")

    safe_valve_setpoint = _require_float("safe_valve_setpoint", data["safe_valve_setpoint"])

    return RigConfig(
        arm_length_m=arm_length_m,
        pedal_a=pedal_a,
        pedal_b=pedal_b,
        pedal_released_v=pedal_released_v,
        safe_valve_setpoint=safe_valve_setpoint,
        heartbeat_timeout_s=heartbeat_timeout_s,
    )


def _read_pedal_table(section: str, table: object) -> PedalLimits:
    if not isinstance(table, dict):
        raise ValueError(section)  # noqa: TRY004

    for key in table:
        if key not in _PEDAL_TABLE_KEYS:
            raise ValueError(key)

    for key in _PEDAL_TABLE_KEYS:
        if key not in table:
            raise ValueError(key)

    minimum_v = _require_float(f"{section}.minimum_v", table["minimum_v"])
    maximum_v = _require_float(f"{section}.maximum_v", table["maximum_v"])
    try:
        return PedalLimits(minimum_v=minimum_v, maximum_v=maximum_v)
    except ValueError as exc:
        raise ValueError(section) from exc


def _require_float(key: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(key)  # noqa: TRY004
    return float(value)
