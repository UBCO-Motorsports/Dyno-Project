import json
from pathlib import Path

import pytest

from dyno import link

CASES = json.loads(
    (Path(__file__).parent / "contract" / "link_cases.json").read_text(
        encoding="utf-8"
    )
)


def _as_dict(message):
    if isinstance(message, link.Setpoint):
        kind = "setpoint"
    elif isinstance(message, link.Heartbeat):
        kind = "heartbeat"
    elif isinstance(message, link.Acknowledge):
        kind = "acknowledge"
    elif isinstance(message, link.Sample):
        kind = "sample"
    elif isinstance(message, link.Fault):
        kind = "fault"
    else:
        raise AssertionError(f"unexpected message: {message!r}")  # noqa: TRY004

    return {"type": kind, **message.__dict__}


@pytest.mark.parametrize(
    "case",
    [case for case in CASES if case["valid"]],
    ids=lambda case: case["name"],
)
def test_contract_valid_lines_decode_to_expected_fields(case):
    message = link.decode(case["line"].encode("utf-8"))
    assert _as_dict(message) == case["expect"]


@pytest.mark.parametrize(
    "case",
    [case for case in CASES if not case["valid"]],
    ids=lambda case: case["name"],
)
def test_contract_invalid_lines_are_rejected(case):
    with pytest.raises(ValueError, match=case["expect"]):
        link.decode(case["line"].encode("utf-8"))


@pytest.mark.parametrize(
    "message_factory",
    [
        pytest.param(lambda: link.Setpoint(1, 0.5, 12.0), id="setpoint"),
        pytest.param(lambda: link.Heartbeat(2), id="heartbeat"),
        pytest.param(lambda: link.Acknowledge(3), id="acknowledge"),
        pytest.param(
            lambda: link.Sample(4, 123456, 10.25, 1200.0, 0.4, 1.2, 1.3, "running"),
            id="sample",
        ),
        pytest.param(
            lambda: link.Fault(5, "heartbeat_timeout", "no heartbeat received"),
            id="fault",
        ),
    ],
)
def test_encode_then_decode_returns_equal_message(message_factory):
    message = message_factory()
    line = link.encode(message)
    assert line.endswith(b"\n")
    assert link.decode(line) == message


@pytest.mark.parametrize(
    "pedal_position",
    [-0.1, 1.1],
    ids=["below-range", "above-range"],
)
def test_encode_rejects_pedal_position_outside_range(pedal_position):
    message = link.Setpoint(1, pedal_position, 0.0)
    with pytest.raises(ValueError, match="pedal_position must be between 0 and 1"):
        link.encode(message)


def test_sequence_tracker_reports_missing_messages():
    tracker = link.SequenceTracker()
    assert tracker.accept(4) == 0
    assert tracker.accept(7) == 2


@pytest.mark.parametrize("seq", [4, 3], ids=["repeated", "older"])
def test_sequence_tracker_rejects_repeated_or_older_sequence(seq):
    tracker = link.SequenceTracker()
    tracker.accept(4)

    with pytest.raises(ValueError, match="repeated or older"):
        tracker.accept(seq)
