from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class RigCommand:
    pedal_voltage_a: float
    pedal_voltage_b: float
    torque_command_nm: float
    valve_setpoint: float


class RunState(Enum):
    IDLE = "idle"
    ARMED = "armed"
    RUNNING = "running"
    SAFE = "safe"


class RunEvent(Enum):
    ARM = "arm"
    START = "start"
    STOP = "stop"
    FAULT = "fault"
    ACKNOWLEDGE = "acknowledge"


_TRANSITIONS: dict[tuple[RunState, RunEvent], RunState] = {
    (RunState.IDLE, RunEvent.ARM): RunState.ARMED,
    (RunState.IDLE, RunEvent.STOP): RunState.IDLE,
    (RunState.IDLE, RunEvent.FAULT): RunState.SAFE,
    (RunState.ARMED, RunEvent.START): RunState.RUNNING,
    (RunState.ARMED, RunEvent.STOP): RunState.IDLE,
    (RunState.ARMED, RunEvent.FAULT): RunState.SAFE,
    (RunState.RUNNING, RunEvent.STOP): RunState.SAFE,
    (RunState.RUNNING, RunEvent.FAULT): RunState.SAFE,
    (RunState.SAFE, RunEvent.FAULT): RunState.SAFE,
    (RunState.SAFE, RunEvent.ACKNOWLEDGE): RunState.IDLE,
}


class TestRun:
    __test__ = False

    def __init__(self, safe_valve_setpoint: float = 0) -> None:
        self._state = RunState.IDLE
        self._safe_valve_setpoint = safe_valve_setpoint

    def state(self) -> RunState:
        return self._state

    def handle(self, event: RunEvent) -> None:
        key = (self._state, event)
        try:
            self._state = _TRANSITIONS[key]
        except KeyError as exc:
            raise ValueError("illegal transition") from exc

    def _safe_command(self) -> RigCommand:
        return RigCommand(
            pedal_voltage_a=0,
            pedal_voltage_b=0,
            torque_command_nm=0,
            valve_setpoint=self._safe_valve_setpoint,
        )

    def command(self, requested: RigCommand) -> RigCommand:
        """In RUNNING, return requested. In SAFE, return the safe command.

        IDLE and ARMED also return the safe command, because the motor is not in a run.
        """
        if self._state is RunState.RUNNING:
            return requested
        return self._safe_command()
