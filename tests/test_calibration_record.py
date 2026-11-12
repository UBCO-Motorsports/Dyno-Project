from datetime import UTC, datetime

import pytest

from dyno.calibration import format_calibration_record

RAW = [0, 1, 2]
REFERENCE = [0, 1, 3]
WHEN_UTC = datetime(2026, 11, 12, 18, 0, 0, tzinfo=UTC)


def test_record_contains_required_fields_and_hand_solved_values():
    text = format_calibration_record(
        sensor_name="example-load-cell",
        when_utc=WHEN_UTC,
        raw_points=RAW,
        reference_points=REFERENCE,
        operator_name="Example Operator",
        arm_length_m=None,
    )
    assert "example-load-cell" in text
    assert "Example Operator" in text
    assert WHEN_UTC.isoformat() in text
    assert "1.5" in text
    assert "0.333" in text
    assert "error is the maximum absolute residual of the calibration points" in text
    assert "not signed" in text
    assert "arm length: not provided" in text


def test_record_lists_each_point_with_residual_in_order():
    text = format_calibration_record(
        sensor_name="example-load-cell",
        when_utc=WHEN_UTC,
        raw_points=RAW,
        reference_points=REFERENCE,
        operator_name="Example Operator",
        arm_length_m=None,
    )
    lines = text.splitlines()
    point_lines = [line for line in lines if line.startswith("point")]
    assert len(point_lines) == 3
    assert "raw 0" in point_lines[0] and "residual" in point_lines[0]
    assert "raw 1" in point_lines[1] and "residual" in point_lines[1]
    assert "raw 2" in point_lines[2] and "residual" in point_lines[2]
    assert "0.167" in point_lines[0] or "0.166" in point_lines[0]
    assert "-0.333" in point_lines[1]
    assert "0.167" in point_lines[2] or "0.166" in point_lines[2]


def test_blank_operator_name_is_rejected():
    with pytest.raises(ValueError, match="operator"):
        format_calibration_record(
            sensor_name="example-load-cell",
            when_utc=WHEN_UTC,
            raw_points=RAW,
            reference_points=REFERENCE,
            operator_name="   ",
            arm_length_m=None,
        )


def test_naive_datetime_is_rejected():
    naive = datetime(2026, 11, 12, 18, 0, 0)
    with pytest.raises(ValueError, match="timezone"):
        format_calibration_record(
            sensor_name="example-load-cell",
            when_utc=naive,
            raw_points=RAW,
            reference_points=REFERENCE,
            operator_name="Example Operator",
            arm_length_m=None,
        )


def test_arm_length_is_included_when_provided():
    text = format_calibration_record(
        sensor_name="example-load-cell",
        when_utc=WHEN_UTC,
        raw_points=RAW,
        reference_points=REFERENCE,
        operator_name="Example Operator",
        arm_length_m=0.25,
    )
    assert "arm length: 0.25 m" in text
    assert "arm length: not provided" not in text
