from enum import Enum


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
