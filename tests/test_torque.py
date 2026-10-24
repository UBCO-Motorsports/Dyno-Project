from dyno.torque import torque_nm

def test_torque_is_force_times_arm_length():
    # Example arm. Not the car's arm.
    assert torque_nm(force_n=100, arm_length_m=0.25) == 25


def test_zero_force_is_zero_torque():
    assert torque_nm(force_n=0, arm_length_m=0.5) == 0