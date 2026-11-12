from pathlib import Path

import pytest

from dyno.rig_config import RigConfig, load_rig_config

VALID_MINIMAL = """\
# EXAMPLE VALUES ONLY.
arm_length_m = 0.5
pedal_released_v = 0.5
safe_valve_setpoint = 0.0
heartbeat_timeout_s = 0.25

[pedal_a]
minimum_v = 0.5
maximum_v = 4.5

[pedal_b]
minimum_v = 0.25
maximum_v = 2.25
"""


def _write_rig(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "rig.toml"
    path.write_text(body, encoding="utf-8")
    return path


def test_example_file_loads_every_field(tmp_path):
    path = _write_rig(tmp_path, VALID_MINIMAL)
    cfg = load_rig_config(path)
    assert cfg.arm_length_m == pytest.approx(0.5)
    assert cfg.pedal_released_v == pytest.approx(0.5)
    assert cfg.safe_valve_setpoint == pytest.approx(0.0)
    assert cfg.heartbeat_timeout_s == pytest.approx(0.25)
    assert cfg.pedal_a.minimum_v == pytest.approx(0.5)
    assert cfg.pedal_a.maximum_v == pytest.approx(4.5)
    assert cfg.pedal_b.minimum_v == pytest.approx(0.25)
    assert cfg.pedal_b.maximum_v == pytest.approx(2.25)


def test_repo_example_toml_loads(tmp_path):
    example = Path(__file__).resolve().parents[1] / "rig.example.toml"
    cfg = load_rig_config(example)
    assert isinstance(cfg, RigConfig)
    assert cfg.arm_length_m == pytest.approx(0.5)
    assert cfg.heartbeat_timeout_s == pytest.approx(0.25)


def test_missing_key_names_that_key(tmp_path):
    body = VALID_MINIMAL.replace("arm_length_m = 0.5\n", "")
    path = _write_rig(tmp_path, body)
    with pytest.raises(ValueError, match="arm_length_m"):
        load_rig_config(path)


def test_arm_length_zero_or_negative_is_rejected(tmp_path):
    path = _write_rig(tmp_path, VALID_MINIMAL.replace("arm_length_m = 0.5", "arm_length_m = 0"))
    with pytest.raises(ValueError, match="arm_length_m"):
        load_rig_config(path)


def test_heartbeat_timeout_zero_or_negative_is_rejected(tmp_path):
    path = _write_rig(
        tmp_path,
        VALID_MINIMAL.replace("heartbeat_timeout_s = 0.25", "heartbeat_timeout_s = 0"),
    )
    with pytest.raises(ValueError, match="heartbeat_timeout_s"):
        load_rig_config(path)


def test_pedal_released_v_outside_pedal_a_range_is_rejected(tmp_path):
    path = _write_rig(tmp_path, VALID_MINIMAL.replace("pedal_released_v = 0.5", "pedal_released_v = 9"))
    with pytest.raises(ValueError, match="pedal_released_v"):
        load_rig_config(path)


def test_wrong_type_is_rejected(tmp_path):
    path = _write_rig(tmp_path, VALID_MINIMAL.replace("arm_length_m = 0.5", 'arm_length_m = "half a metre"'))
    with pytest.raises(ValueError, match="arm_length_m"):
        load_rig_config(path)


def test_unknown_extra_key_is_rejected(tmp_path):
    path = _write_rig(tmp_path, VALID_MINIMAL + "\narm_lenght_m = 0.5\n")
    with pytest.raises(ValueError, match="arm_lenght_m"):
        load_rig_config(path)
