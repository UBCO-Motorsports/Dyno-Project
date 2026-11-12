import math

import pytest

from dyno.calibration import apply_calibration


def test_apply_uses_gain_and_offset():
    assert apply_calibration(raw=4, gain=2, offset=0.5) == pytest.approx(8.5)


def test_apply_matches_a_fitted_line():
    # (0,0), (10,25), (20,50) is gain 2.5, offset 0; raw 4 → 10 (pending #7 for fit_calibration_line)
    assert apply_calibration(raw=4, gain=2.5, offset=0) == pytest.approx(10)


def test_apply_rejects_non_finite_numbers():
    with pytest.raises(ValueError, match="finite"):
        apply_calibration(raw=math.nan, gain=1, offset=0)
