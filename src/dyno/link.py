"""JSON-lines protocol between the laptop and the real-time controller."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True)
class Setpoint:
    seq: int
    pedal_position: float
    valve_setpoint: float


@dataclass(frozen=True)
class Heartbeat:
    seq: int


@dataclass(frozen=True)
class Acknowledge:
    seq: int


@dataclass(frozen=True)
class Sample:
    seq: int
    controller_time_us: int
    load_raw: float
    speed_rpm: float
    valve_position: float
    pedal_voltage_a: float
    pedal_voltage_b: float
    state: str


@dataclass(frozen=True)
class Fault:
    seq: int
    code: str
    detail: str


Message: TypeAlias = Setpoint | Heartbeat | Acknowledge | Sample | Fault


_FIELDS: dict[str, tuple[str, ...]] = {
    "setpoint": ("seq", "pedal_position", "valve_setpoint"),
    "heartbeat": ("seq",),
    "acknowledge": ("seq",),
    "sample": (
        "seq",
        "controller_time_us",
        "load_raw",
        "speed_rpm",
        "valve_position",
        "pedal_voltage_a",
        "pedal_voltage_b",
        "state",
    ),
    "fault": ("seq", "code", "detail"),
}


def _number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")  # noqa: TRY004
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{field} must be a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field} must be a finite number")
    return result


def _integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer")  # noqa: TRY004
    if value < 0:
        raise ValueError(f"{field} must be non-negative")
    return value


def _message_from_dict(data: object) -> Message:
    if not isinstance(data, dict):
        raise ValueError("message must be a JSON object")  # noqa: TRY004

    kind = data.get("type")
    if not isinstance(kind, str) or kind not in _FIELDS:
        raise ValueError(f"unknown type: {kind!r}")

    required = set(_FIELDS[kind])
    missing = required - data.keys()
    if missing:
        raise ValueError(f"missing field: {min(missing)}")

    extra = data.keys() - (required | {"type"})
    if extra:
        raise ValueError(f"unexpected field: {min(extra)}")

    seq = _integer(data["seq"], "seq")

    if kind == "setpoint":
        pedal = _number(data["pedal_position"], "pedal_position")
        if not 0.0 <= pedal <= 1.0:
            raise ValueError("pedal_position must be between 0 and 1")
        return Setpoint(seq, pedal, _number(data["valve_setpoint"], "valve_setpoint"))

    if kind == "heartbeat":
        return Heartbeat(seq)
    if kind == "acknowledge":
        return Acknowledge(seq)

    if kind == "sample":
        if not isinstance(data["state"], str):
            raise ValueError("state must be a string")
        return Sample(
            seq=seq,
            controller_time_us=_integer(data["controller_time_us"], "controller_time_us"),
            load_raw=_number(data["load_raw"], "load_raw"),
            speed_rpm=_number(data["speed_rpm"], "speed_rpm"),
            valve_position=_number(data["valve_position"], "valve_position"),
            pedal_voltage_a=_number(data["pedal_voltage_a"], "pedal_voltage_a"),
            pedal_voltage_b=_number(data["pedal_voltage_b"], "pedal_voltage_b"),
            state=data["state"],
        )

    if not isinstance(data["code"], str):
        raise ValueError("code must be a string")  # noqa: TRY004
    if not isinstance(data["detail"], str):
        raise ValueError("detail must be a string")  # noqa: TRY004
    return Fault(seq, data["code"], data["detail"])


def _message_dict(message: object) -> dict[str, object]:
    if isinstance(message, Setpoint):
        kind = "setpoint"
    elif isinstance(message, Heartbeat):
        kind = "heartbeat"
    elif isinstance(message, Acknowledge):
        kind = "acknowledge"
    elif isinstance(message, Sample):
        kind = "sample"
    elif isinstance(message, Fault):
        kind = "fault"
    else:
        raise ValueError(f"unsupported message object: {type(message).__name__}")  # noqa: TRY004

    data = {"type": kind, **message.__dict__}
    _message_from_dict(data)
    return data


def encode(message: Message) -> bytes:
    """Encode one message as UTF-8 JSON followed by a newline."""
    data = _message_dict(message)
    try:
        text = json.dumps(data, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"message cannot be encoded: {exc}") from exc
    return text.encode("utf-8") + b"\n"


def decode(line: bytes) -> Message:
    """Decode one newline-delimited JSON message."""
    if not isinstance(line, bytes):
        raise ValueError("line must be bytes")  # noqa: TRY004
    try:
        text = line.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("line is not valid UTF-8") from exc
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"line is not valid JSON: {exc}") from exc
    return _message_from_dict(data)


class SequenceTracker:
    """Reject repeated or old sequence numbers and report gaps."""

    def __init__(self) -> None:
        self._last: int | None = None

    def accept(self, seq: int) -> int:
        """Accept a sequence number and return how many messages were missed."""
        seq = _integer(seq, "seq")
        if self._last is not None and seq <= self._last:
            raise ValueError(f"sequence {seq} is repeated or older than {self._last}")
        missed = 0 if self._last is None else seq - self._last - 1
        self._last = seq
        return missed
