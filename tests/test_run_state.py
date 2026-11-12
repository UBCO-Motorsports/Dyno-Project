import pytest

from dyno.run_state import RunEvent, RunState, TestRun


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
