import math

import pytest

from dyno.pedal import (
    PedalLimits,
    clamp_pedal,
    pedal_voltages,
    pedals_agree,
    stopped_pedal,
)

EXAMPLE = PedalLimits(minimum_v=0.5, maximum_v=4.5)

# example only — confirm on bench before driving the real VCU (#5, question 7)
A = PedalLimits(minimum_v=0.5, maximum_v=4.5)
B = PedalLimits(minimum_v=0.25, maximum_v=2.25)


def test_inside_the_example_range_is_unchanged():
    assert clamp_pedal(1.2, EXAMPLE) == pytest.approx(1.2)


def test_outside_the_range_is_clamped():
    assert clamp_pedal(9, EXAMPLE) == pytest.approx(4.5)
    assert clamp_pedal(-1, EXAMPLE) == pytest.approx(0.5)


def test_stopped_pedal_is_zero():
    assert stopped_pedal() == (0.0, 0.0)


def test_inverted_limits_are_rejected():
    with pytest.raises(ValueError, match="limits"):
        PedalLimits(minimum_v=4, maximum_v=1)


def test_non_finite_limits_are_rejected():
    with pytest.raises(ValueError, match="limits"):
        PedalLimits(minimum_v=math.nan, maximum_v=4.5)
    with pytest.raises(ValueError, match="limits"):
        PedalLimits(minimum_v=0.5, maximum_v=math.inf)


def test_released_is_each_channel_minimum():
    assert pedal_voltages(0.0, A, B) == pytest.approx((0.5, 0.25))


def test_quarter_pedal_on_both_channels():
    # A: 0.5 + 0.25 * 4.0 = 1.5 V. B: 0.25 + 0.25 * 2.0 = 0.75 V.
    assert pedal_voltages(0.25, A, B) == pytest.approx((1.5, 0.75))


def test_position_outside_zero_to_one_is_rejected():
    with pytest.raises(ValueError, match="position"):
        pedal_voltages(1.2, A, B)


def test_generated_voltages_always_agree():
    for step in range(11):
        assert pedals_agree(*pedal_voltages(step / 10, A, B), A, B)


def test_eleven_points_apart_disagree():
    # A at 0.50 -> 2.5 V. B at 0.61 -> 1.47 V.
    assert not pedals_agree(2.5, 1.47, A, B)
