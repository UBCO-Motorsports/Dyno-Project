import math

import pytest

from dyno.calibration import (
    apply_calibration,
    calibration_residuals,
    fit_calibration_line,
    maximum_abs_residual,
)


def test_points_on_a_line_give_that_line():
    gain, offset = fit_calibration_line([0, 10, 20], [0, 25, 50])
    assert gain == pytest.approx(2.5)
    assert offset == pytest.approx(0)


def test_points_off_a_line_give_the_least_squares_line():
    # Hand-solved: mean raw 1, mean reference 4/3, slope 3/2, offset 4/3 - 3/2 = -1/6.
    gain, offset = fit_calibration_line([0, 1, 2], [0, 1, 3])
    assert gain == pytest.approx(1.5)
    assert offset == pytest.approx(-1 / 6)


def test_fewer_than_three_points_are_rejected():
    with pytest.raises(ValueError, match="three"):
        fit_calibration_line([0, 10], [0, 25])


def test_lists_of_different_length_are_rejected():
    with pytest.raises(ValueError, match="same length"):
        fit_calibration_line([0, 1, 2], [0, 1])


def test_identical_raw_values_are_rejected():
    with pytest.raises(ValueError, match="distinct"):
        fit_calibration_line([4, 4, 4], [1, 2, 3])


def test_non_finite_points_are_rejected():
    with pytest.raises(ValueError, match="finite"):
        fit_calibration_line([0, math.nan, 2], [0, 1, 2])


def test_apply_uses_gain_and_offset():
    assert apply_calibration(raw=4, gain=2, offset=0.5) == pytest.approx(8.5)


def test_apply_matches_a_fitted_line():
    gain, offset = fit_calibration_line([0, 10, 20], [0, 25, 50])
    assert apply_calibration(raw=4, gain=gain, offset=offset) == pytest.approx(10)


def test_apply_rejects_non_finite_numbers():
    with pytest.raises(ValueError, match="finite"):
        apply_calibration(raw=math.nan, gain=1, offset=0)


def test_residuals_of_the_hand_solved_fit():
    # Line from #7: gain 1.5, offset -1/6. Predictions -1/6, 4/3, 17/6.
    raw, reference = [0, 1, 2], [0, 1, 3]
    gain, offset = fit_calibration_line(raw, reference)
    residuals = calibration_residuals(raw, reference, gain, offset)
    assert residuals == pytest.approx([1 / 6, -1 / 3, 1 / 6])
    assert maximum_abs_residual(residuals) == pytest.approx(1 / 3)


def test_maximum_is_taken_by_size_not_sign():
    assert maximum_abs_residual([0.1, -0.4, 0.2]) == pytest.approx(0.4)


def test_empty_residuals_are_rejected():
    with pytest.raises(ValueError, match="residual"):
        maximum_abs_residual([])


def test_non_finite_residual_is_rejected():
    with pytest.raises(ValueError, match="finite"):
        maximum_abs_residual([0.1, math.nan])
