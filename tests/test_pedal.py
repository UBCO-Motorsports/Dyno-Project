import pytest

from dyno.pedal import PedalLimits, clamp_pedal, stopped_pedal

EXAMPLE = PedalLimits(minimum_v=0.5, maximum_v=4.5)


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
