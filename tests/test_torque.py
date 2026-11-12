import math

import pytest

from dyno.torque import torque_nm


def test_torque_is_force_times_arm_length():
    # Example arm. Not the car's arm.
    assert torque_nm(force_n=100, arm_length_m=0.25) == 25


def test_zero_force_is_zero_torque():
    assert torque_nm(force_n=0, arm_length_m=0.5) == 0


def test_arm_length_must_be_positive():
    with pytest.raises(ValueError, match="arm length"):
        torque_nm(force_n=10, arm_length_m=0)
    with pytest.raises(ValueError, match="arm length"):
        torque_nm(force_n=10, arm_length_m=-0.2)


def test_torque_rejects_non_finite_numbers():
    with pytest.raises(ValueError, match="finite"):
        torque_nm(force_n=math.nan, arm_length_m=0.3)
    with pytest.raises(ValueError, match="finite"):
        torque_nm(force_n=10, arm_length_m=math.inf)
