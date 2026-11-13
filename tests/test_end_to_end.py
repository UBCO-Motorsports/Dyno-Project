"""Whole supervisor flow on the simulator (#45)."""

from __future__ import annotations

import itertools
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from dyno.log_csv import read_log, write_log
from dyno.power import mechanical_power_kw
from dyno.readout import OperatorSession
from dyno.rig_config import load_rig_config
from dyno.run_state import RigCommand, RunState, TestRun
from dyno.sample import Sample
from dyno.simulator import DynoSimulator
from dyno.torque import torque_nm

_REPO_ROOT = Path(__file__).resolve().parents[1]
_EXAMPLE_RIG = _REPO_ROOT / "rig.example.toml"

_DT_S = 0.01
_RUN_DURATION_S = 5.0
_POST_STOP_DURATION_S = 1.0
_SAMPLE_INTERVAL_S = 0.1

_MANUAL_PEDAL_POSITION = 0.25
_MANUAL_VALVE_SETPOINT = 0.4


def _sample_from_plant(
    sim: DynoSimulator,
    session: OperatorSession,
    commanded: RigCommand,
    arm_length_m: float,
    t0: datetime,
    elapsed_s: float,
) -> Sample:
    return Sample(
        timestamp_utc=t0 + timedelta(seconds=elapsed_s),
        torque_nm=torque_nm(sim.force_n(), arm_length_m),
        speed_rpm=sim.speed_rpm(),
        strain=0.0,
        valve_setpoint=commanded.valve_setpoint,
        pedal_voltage_a=commanded.pedal_voltage_a,
        pedal_voltage_b=commanded.pedal_voltage_b,
        run_state=session.run.state().value,
    )


def _run_simulator_flow(tmp_path: Path, *, apply_stop: bool = True) -> list[Sample]:
    config = load_rig_config(_EXAMPLE_RIG)
    sim = DynoSimulator(
        arm_length_m=config.arm_length_m,
        pedal_limits_a=config.pedal_a,
        pedal_limits_b=config.pedal_b,
    )
    session = OperatorSession(
        run=TestRun(safe_valve_setpoint=config.safe_valve_setpoint),
        sample=Sample(
            timestamp_utc=datetime(2026, 11, 13, 12, 0, tzinfo=UTC),
            torque_nm=0.0,
            speed_rpm=0.0,
            strain=0.0,
            valve_setpoint=0.0,
            pedal_voltage_a=0.0,
            pedal_voltage_b=0.0,
            run_state="idle",
        ),
    )

    session.arm()
    session.start()
    commanded = session.manual_command(
        _MANUAL_PEDAL_POSITION,
        _MANUAL_VALVE_SETPOINT,
        config.pedal_a,
        config.pedal_b,
    )
    sim.apply_command(commanded)

    t0 = datetime(2026, 11, 13, 12, 0, tzinfo=UTC)
    samples: list[Sample] = []
    run_steps = int(_RUN_DURATION_S / _DT_S)
    record_every = int(_SAMPLE_INTERVAL_S / _DT_S)

    for step in range(1, run_steps + 1):
        sim.step(_DT_S)
        if step % record_every == 0:
            samples.append(
                _sample_from_plant(
                    sim, session, commanded, config.arm_length_m, t0, step * _DT_S
                )
            )

    if apply_stop:
        session.stop()
    commanded = session.manual_command(
        _MANUAL_PEDAL_POSITION,
        _MANUAL_VALVE_SETPOINT,
        config.pedal_a,
        config.pedal_b,
    )
    sim.apply_command(commanded)

    post_stop_steps = int(_POST_STOP_DURATION_S / _DT_S)
    for step in range(1, post_stop_steps + 1):
        sim.step(_DT_S)
        if step % record_every == 0:
            elapsed_s = _RUN_DURATION_S + step * _DT_S
            samples.append(
                _sample_from_plant(
                    sim, session, commanded, config.arm_length_m, t0, elapsed_s
                )
            )

    write_log(tmp_path / "run.csv", samples)
    return read_log(tmp_path / "run.csv")


def test_end_to_end_simulator_flow(tmp_path: Path) -> None:
    started = time.monotonic()
    rows = _run_simulator_flow(tmp_path)
    assert time.monotonic() - started < 2.0

    for row in rows:
        assert row.power_kw == pytest.approx(
            mechanical_power_kw(row.torque_nm, row.speed_rpm), abs=1e-9
        )

    running = [r for r in rows if r.run_state == RunState.RUNNING.value]
    assert len(running) >= 2
    assert running[-1].speed_rpm > running[0].speed_rpm

    safe_rows = [r for r in rows if r.run_state == RunState.SAFE.value]
    assert safe_rows, "expected samples after stop"

    config = load_rig_config(_EXAMPLE_RIG)
    safe_valve = config.safe_valve_setpoint
    for row in safe_rows:
        assert row.pedal_voltage_a == pytest.approx(0.0)
        assert row.pedal_voltage_b == pytest.approx(0.0)
        assert row.valve_setpoint == pytest.approx(safe_valve)

    peak_speed = max(r.speed_rpm for r in running)
    for row in safe_rows:
        assert row.speed_rpm <= peak_speed + 1e-9

    for prev, curr in itertools.pairwise(r.speed_rpm for r in safe_rows):
        assert curr <= prev + 1e-9

    assert rows[-1].run_state == RunState.SAFE.value
