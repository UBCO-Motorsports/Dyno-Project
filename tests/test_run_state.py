import pytest

from dyno.run_state import RigCommand, RunEvent, RunState, TestRun

# 0.0 in tests is an example only — not a claim about the physical valve position.
_REQUESTED = RigCommand(1.2, 1.1, 40, 0.9)


def test_safe_command_is_zero_pedal_and_zero_torque():
    run = TestRun(safe_valve_setpoint=0.25)
    run.handle(RunEvent.FAULT)
    commanded = run.command(RigCommand(1.2, 1.1, 40, 0.9))
    assert commanded == RigCommand(0, 0, 0, 0.25)


def test_running_passes_the_request_through():
    run = TestRun(safe_valve_setpoint=0)  # example setpoint; not a physical valve claim
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.START)
    requested = RigCommand(0.4, 0.4, 15, 0.3)
    assert run.command(requested) == requested


def test_stop_from_running_commands_safe():
    run = TestRun(safe_valve_setpoint=0.25)
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.START)
    run.handle(RunEvent.STOP)
    assert run.command(_REQUESTED) == RigCommand(0, 0, 0, 0.25)


def test_fault_from_armed_commands_safe():
    run = TestRun(safe_valve_setpoint=0.25)
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.FAULT)
    assert run.command(_REQUESTED) == RigCommand(0, 0, 0, 0.25)


def test_fault_from_running_commands_safe():
    run = TestRun(safe_valve_setpoint=0.25)
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.START)
    run.handle(RunEvent.FAULT)
    assert run.command(_REQUESTED) == RigCommand(0, 0, 0, 0.25)


def test_fault_from_idle_commands_safe():
    run = TestRun(safe_valve_setpoint=0.25)
    run.handle(RunEvent.FAULT)
    assert run.command(_REQUESTED) == RigCommand(0, 0, 0, 0.25)


def test_idle_does_not_pass_torque_request_through():
    run = TestRun(safe_valve_setpoint=0.25)
    assert run.command(_REQUESTED) == RigCommand(0, 0, 0, 0.25)


def test_armed_does_not_pass_torque_request_through():
    run = TestRun(safe_valve_setpoint=0.25)
    run.handle(RunEvent.ARM)
    assert run.command(_REQUESTED) == RigCommand(0, 0, 0, 0.25)


def test_idle_arm_becomes_armed():
    run = TestRun()
    run.handle(RunEvent.ARM)
    assert run.state() is RunState.ARMED


def test_idle_stop_stays_idle():
    run = TestRun()
    run.handle(RunEvent.STOP)
    assert run.state() is RunState.IDLE


def test_idle_fault_becomes_safe():
    run = TestRun()
    run.handle(RunEvent.FAULT)
    assert run.state() is RunState.SAFE


def test_armed_start_becomes_running():
    run = TestRun()
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.START)
    assert run.state() is RunState.RUNNING


def test_armed_stop_returns_idle():
    run = TestRun()
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.STOP)
    assert run.state() is RunState.IDLE


def test_armed_fault_becomes_safe():
    run = TestRun()
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.FAULT)
    assert run.state() is RunState.SAFE


def test_running_stop_becomes_safe():
    run = TestRun()
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.START)
    run.handle(RunEvent.STOP)
    assert run.state() is RunState.SAFE


def test_running_fault_becomes_safe():
    run = TestRun()
    run.handle(RunEvent.ARM)
    run.handle(RunEvent.START)
    run.handle(RunEvent.FAULT)
    assert run.state() is RunState.SAFE


def test_safe_fault_stays_safe():
    run = TestRun()
    run.handle(RunEvent.FAULT)
    run.handle(RunEvent.FAULT)
    assert run.state() is RunState.SAFE


def test_safe_acknowledge_returns_idle():
    run = TestRun()
    run.handle(RunEvent.FAULT)
    run.handle(RunEvent.ACKNOWLEDGE)
    assert run.state() is RunState.IDLE


def test_start_from_idle_is_illegal():
    run = TestRun()
    with pytest.raises(ValueError, match="illegal"):
        run.handle(RunEvent.START)
    assert run.state() is RunState.IDLE


def test_new_test_run_starts_idle():
    run = TestRun()
    assert run.state() is RunState.IDLE
