import math


def torque_nm(force_n: float, arm_length_m: float) -> float:
    if not (math.isfinite(force_n) and math.isfinite(arm_length_m)):
        raise ValueError("force and arm length must be finite numbers")
    if arm_length_m <= 0:
        raise ValueError("arm length must be greater than zero")
    return force_n * arm_length_m
