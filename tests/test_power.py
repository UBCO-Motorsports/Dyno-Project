import math

from dyno.power import mechanical_power_kw


def test_power_matches_the_hand_calculation():
    # 10 N·m at 1000 rpm.
    expected = 10 * 1000 * 2 * math.pi / 60_000
    assert math.isclose(mechanical_power_kw(10, 1000), expected, rel_tol=1e-12)


def test_power_is_reported_even_when_it_is_above_the_80_kw_cap():
    # 150 N·m at 7000 rpm is above the operating cap. Do not clip it.
    expected = 150 * 7000 * 2 * math.pi / 60_000
    assert expected > 80
    assert math.isclose(mechanical_power_kw(150, 7000), expected, rel_tol=1e-12)
