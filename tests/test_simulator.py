"""Behaviour tests for the rig simulator (#41)."""

import itertools
import math

import pytest

from dyno.limits import MAX_SPEED_RPM, PEAK_TORQUE_NM
from dyno.pedal import PedalLimits
from dyno.ports import ForceSource, PedalOutput, SpeedSource, Valve
from dyno.run_state import RigCommand, RunEvent, RunState, TestRun
from dyno.simulator import DynoSimulator

# Example rig bounds from rig.example.toml — not physical claims.
_PEDAL_A = PedalLimits(minimum_v=0.5, maximum_v=4.5)
_PEDAL_B = PedalLimits(minimum_v=0.25, maximum_v=2.25)
_EXAMPLE_ARM_LENGTH_M = 0.5

# Defaults chosen with the simulator docstring: k=6e-4 keeps ss speed below 7000 rpm
# at pedal=1.0 and fill=0.5; c=0 isolates the steady-state identity in behaviour 3.
_EXAMPLE_K = 6e-4
_EXAMPLE_C = 0.0
_EXAMPLE_J = 0.1

_DT_S = 0.01
_SETTLE_STEPS = 8000


def _sim(**kwargs: float) -> DynoSimulator:
    return DynoSimulator(
        arm_length_m=_EXAMPLE_ARM_LENGTH_M,
        k=_EXAMPLE_K,
        c=_EXAMPLE_C,
        J=_EXAMPLE_J,
        **kwargs,
    )


def _read_force(source: ForceSource) -> float:
    return source.force_n()


def _read_speed(source: SpeedSource) -> float:
    return source.speed_rpm()


def _settle(sim: DynoSimulator, steps: int = _SETTLE_STEPS) -> None:
    for _ in range(steps):
        sim.step(_DT_S)


def _running_command(pedal_position: float, fill: float) -> RigCommand:
    """Map example pedal position 0–1 and valve fill to a RigCommand."""
    va = _PEDAL_A.minimum_v + pedal_position * (_PEDAL_A.maximum_v - _PEDAL_A.minimum_v)
    vb = _PEDAL_B.minimum_v + pedal_position * (_PEDAL_B.maximum_v - _PEDAL_B.minimum_v)
    # torque_command_nm>0 marks an intentional motor request while RUNNING
    return RigCommand(va, vb, PEAK_TORQUE_NM * pedal_position, fill)


def test_simulator_satisfies_hardware_ports():
    sim = _sim()

    def use_ports(
        force: ForceSource,
        speed: SpeedSource,
        valve: Valve,
        pedal: PedalOutput,
    ) -> tuple[float, float, float, tuple[float, float]]:
        valve.set_setpoint(0.2)
        pedal.set_voltages(1.0, 1.0)
        return (
            _read_force(force),
            _read_speed(speed),
            valve.position(),
            pedal.voltages(),
        )

    force_n, rpm, fill, volts = use_ports(sim, sim, sim, sim)
    assert fill == pytest.approx(0.2)
    assert volts == (1.0, 1.0)
    assert isinstance(force_n, float)
    assert isinstance(rpm, float)


def test_zero_pedal_from_standstill_speed_stays_zero():
    sim = _sim()
    sim.set_setpoint(0.5)
    sim.set_voltages(0.0, 0.0)
    for _ in range(500):
        sim.step(_DT_S)
    assert sim.speed_rpm() == pytest.approx(0.0, abs=1e-9)


def test_steady_state_speed_matches_hand_derived_omega():
    # pedal 0.5 → T_m = 75 N·m; fill 0.5; k=6e-4 → k×fill = 3e-4.
    # ω_ss = sqrt(75 / 3e-4) = sqrt(250000) = 500 rad/s (c=0 steady-state identity).
    omega_ss_rad_s = 500.0
    rpm_ss = omega_ss_rad_s * 60.0 / (2.0 * math.pi)

    sim = _sim()
    cmd = _running_command(0.5, 0.5)
    sim.apply_command(cmd)
    _settle(sim)
    assert sim.speed_rpm() == pytest.approx(rpm_ss, rel=0.01)
    assert sim.speed_rpm() < MAX_SPEED_RPM


def test_more_fill_at_same_pedal_yields_lower_steady_speed():
    sim_low_fill = _sim()
    sim_low_fill.apply_command(_running_command(0.8, 0.3))
    _settle(sim_low_fill)
    rpm_low_fill = sim_low_fill.speed_rpm()

    sim_high_fill = _sim()
    sim_high_fill.apply_command(_running_command(0.8, 0.7))
    _settle(sim_high_fill)
    rpm_high_fill = sim_high_fill.speed_rpm()

    assert rpm_high_fill < rpm_low_fill


def test_load_cell_force_times_arm_equals_brake_torque():
    sim = _sim()
    sim.apply_command(_running_command(0.6, 0.4))
    _settle(sim)
    force_n = sim.force_n()
    omega_rad_s = sim.speed_rpm() * 2.0 * math.pi / 60.0
    fill = sim.position()
    brake_torque_nm = _EXAMPLE_K * fill * omega_rad_s**2
    assert force_n * _EXAMPLE_ARM_LENGTH_M == pytest.approx(brake_torque_nm, rel=1e-6)


def test_identical_inputs_give_identical_results():
    cmd = _running_command(0.7, 0.35)

    def run_once() -> tuple[float, float]:
        sim = _sim()
        sim.apply_command(cmd)
        _settle(sim)
        return sim.speed_rpm(), sim.force_n()

    first = run_once()
    second = run_once()
    assert first == second


def test_after_safe_command_speed_only_falls():
    # Safe valve stays partially open (example 0.3) so brake torque can spool the shaft down.
    sim = _sim()
    run = TestRun(safe_valve_setpoint=0.3)
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.START)
    sim.apply_command(run.command(_running_command(1.0, 0.5)))
    _settle(sim, steps=6000)
    rpm_before = sim.speed_rpm()
    assert rpm_before > 100.0
    assert rpm_before < MAX_SPEED_RPM

    run.handle(RunEvent.STOP)
    sim.apply_command(run.command(_running_command(1.0, 0.5)))
    falling: list[float] = [rpm_before]
    for _ in range(400):
        sim.step(_DT_S)
        falling.append(sim.speed_rpm())

    assert falling[-1] < falling[0]
    for prev, curr in itertools.pairwise(falling):
        assert curr <= prev + 1e-9
    assert run.state() is RunState.SAFE
