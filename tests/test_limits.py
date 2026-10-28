from dyno.limits import (
    MAX_SPEED_RPM,
    MIN_STRAIN_SAMPLE_HZ,
    PEAK_TORQUE_NM,
    POWER_CAP_KW,
    exceeds_power_cap,
)


def test_limits_match_the_agreed_envelope():
    assert PEAK_TORQUE_NM == 150
    assert MAX_SPEED_RPM == 7000
    assert POWER_CAP_KW == 80
    assert MIN_STRAIN_SAMPLE_HZ == 10


def test_power_at_the_cap_is_over_the_limit():
    assert exceeds_power_cap(80) is True
    assert exceeds_power_cap(80.0) is True


def test_power_below_the_cap_is_allowed():
    assert exceeds_power_cap(79.999) is False
    