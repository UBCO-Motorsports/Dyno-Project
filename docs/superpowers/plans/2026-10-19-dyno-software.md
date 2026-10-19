# Dyno Software Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the UBCO Motorsports team a tested laptop-side dyno program that measures torque and speed, computes power, logs CSV runs, plays pedal and load profiles, and drops to a safe command if the laptop stops.

**Architecture:** Pure functions and records are tested without hardware. A finite state machine owns run transitions. Sensor and actuator drivers are interfaces with fakes. The laptop is the supervisor. It is not the emergency stop.

**Tech Stack:** Python 3.11+, pytest, CSV in the standard library, tkinter for the later window. No CAN hardware library in the first decoder. No microcontroller firmware until these interfaces are stable.

The team executes this plan from the GitHub issues. Those issues contain the tests, the review gate, and the weekly report. This file is the map and the contract the issues share.

## Global Constraints

- `P (kW) = T (N·m) × speed (rpm) × 2π / 60,000`
- `T (N·m) = F (N) × arm length (m)`
- Peak torque 150 N·m, maximum speed 7000 rpm, power capped below 80 kW
- The power function does not clip. `exceeds_power_cap` is true at or above 80 kW
- Direct shaft coupling, not the chain drive mentioned in the original background
- Strain sample rate at least 10 Hz
- Log rate is the minimum of the speed, torque, and strain rates
- Speed rate follows the VCU once Electrical names it
- Energy source is the vehicle tractive battery
- Procedure CSV header is `time_s,pedal_voltage_a,pedal_voltage_b,load_setpoint`
- Log columns are the `LOG_COLUMNS` tuple in the README
- Stop and fault command zero pedal, zero torque, and the injected safe valve setpoint, with no laptop-side ramp
- TBC numbers stay function arguments until the person named in `docs/open-questions.md` answers
- Unit tests do not touch the rig, the battery, or a guessed CAN id
- Python `>=3.11`

## File structure

| File | Responsibility |
| --- | --- |
| `src/dyno/power.py` | Mechanical power |
| `src/dyno/torque.py` | Force times arm length |
| `src/dyno/limits.py` | Named envelope and cap check |
| `src/dyno/log_schema.py` | Log header contract |
| `src/dyno/calibration.py` | Line, apply, residual, text record |
| `src/dyno/sample.py` | Frozen sample, derived power |
| `src/dyno/log_csv.py` | Write and read a run |
| `src/dyno/summary.py` | Min, max, arithmetic mean |
| `src/dyno/profile.py` | Load and interpolate a procedure |
| `src/dyno/run_state.py` | State machine and safe command |
| `src/dyno/runner.py` | Play a profile through the state machine |
| `src/dyno/timing.py` | Log rate |
| `src/dyno/ports.py` | Protocols for sensors and outputs |
| `src/dyno/valve.py` | Commanded versus achieved |
| `src/dyno/pedal.py` | Clamp and released pedal |
| `src/dyno/can_decode.py` | Bit field to engineering value, speed compare |
| `src/dyno/readout.py` | Readout text and operator session |
| `src/dyno/operator_app.py` | Thin tkinter window |
| `src/dyno/watchdog.py` | Heartbeat timeout |
| `docs/open-questions.md` | Answers from the named people |

## Shared interfaces

Later tasks must use these names.

```python
def mechanical_power_kw(torque_nm: float, speed_rpm: float) -> float: ...
def torque_nm(force_n: float, arm_length_m: float) -> float: ...
def exceeds_power_cap(power_kw: float) -> bool: ...
def calibration_line(raw_1: float, reference_1: float, raw_2: float, reference_2: float) -> tuple[float, float]: ...
def apply_calibration(raw: float, gain: float, offset: float) -> float: ...
def maximum_abs_residual(residuals: list[float]) -> float: ...
def write_log(path: Path, samples: list[Sample]) -> None: ...
def read_log(path: Path) -> list[Sample]: ...
def summarise(samples: list[Sample]) -> LogSummary: ...
def load_profile(path: Path) -> tuple[ProfilePoint, ...]: ...
def sample_profile(points: tuple[ProfilePoint, ...], time_s: float) -> ProfilePoint: ...
def play_profile(run: TestRun, points: tuple[ProfilePoint, ...], times_s: list[float]) -> list[RigCommand]: ...
def log_rate_hz(speed_hz: float, torque_hz: float, strain_hz: float) -> float: ...
def within_tolerance(commanded: float, achieved: float, tolerance: float) -> bool: ...
def clamp_pedal(voltage: float, limits: PedalLimits) -> float: ...
def stopped_pedal() -> tuple[float, float]: ...
def decode_signal(payload: bytes, signal: SignalDef) -> float: ...
def speeds_agree(decoded_rpm: float, reference_rpm: float, tolerance_rpm: float) -> bool: ...
def readout_text(sample: Sample) -> str: ...
def heartbeat_expired(last_seen_s: float, now_s: float, timeout_s: float) -> bool: ...
```

`RunState` values: `idle`, `armed`, `running`, `safe`.

`RunEvent` values: `arm`, `start`, `stop`, `fault`, `acknowledge`.

`RigCommand` fields: `pedal_voltage_a`, `pedal_voltage_b`, `torque_command_nm`, `valve_setpoint`.

## Tasks

Each task is one GitHub issue. The issue body is the test script and the review gate. Order below is the learning order, which is also the kanban order inside each column.

- [ ] **Task 1 — Power.** `tests/test_power.py`, `src/dyno/power.py`. 10 N·m at 1000 rpm matches the formula. 150 N·m at 7000 rpm is above 80 and is not clipped.
- [ ] **Task 2 — Torque.** `tests/test_torque.py`, `src/dyno/torque.py`. 100 N at 0.25 m is 25 N·m. Arm length in the test is an example.
- [ ] **Task 3 — Limits.** `tests/test_limits.py`, `src/dyno/limits.py`. Constants 150, 7000, 80, 10. Cap check is true at 80.
- [ ] **Task 4 — Log columns.** `tests/test_log_schema.py`, `src/dyno/log_schema.py`. The nine-column tuple.
- [ ] **Task 5 — Open questions.** Fill `docs/open-questions.md` by asking Owen, Alex, Electrical, Mechanical, and the safety sign-off owners.
- [ ] **Task 6 — Reject bad inputs.** Non-positive arm length, non-finite numbers, negative speed. Negative torque stays visible.
- [ ] **Task 7 — Calibration line.** Gain and offset from two points. Equal raw values rejected.
- [ ] **Task 8 — Residual uncertainty.** Maximum absolute residual. Empty list rejected.
- [ ] **Task 9 — Apply calibration.** `gain * raw + offset`, shared by strain and force.
- [ ] **Task 10 — Sample record.** Frozen dataclass. Power property. Naive timestamps rejected.
- [ ] **Task 11 — Write CSV.** Header, ISO-8601 UTC, `\n` only.
- [ ] **Task 12 — Read CSV.** Round-trip. Tampered power cell rejected.
- [ ] **Task 13 — Summarise.** Min, max, arithmetic mean. Empty log rejected.
- [ ] **Task 14 — Malformed logs.** `LogFormatError` for empty, column, number, timestamp.
- [ ] **Task 15 — Load profile.** Strictly increasing time, at least two points.
- [ ] **Task 16 — Interpolate.** Flat hold, halfway sweep, clamp ends, 20-row replay.
- [ ] **Task 17 — State machine.** The transition table. Illegal start leaves the state unchanged.
- [ ] **Task 18 — Safe command.** Stop and fault zero pedal and torque.
- [ ] **Task 19 — Play profile.** Running sweep versus safe command after stop.
- [ ] **Task 20 — Log rate.** Minimum rate. Strain below 10 Hz rejected.
- [ ] **Task 21 — Ports.** Protocols and fakes. No drivers.
- [ ] **Task 22 — Valve tolerance.** Absolute tolerance argument. No stored default.
- [ ] **Task 23 — Pedal clamp.** Example limits only in the test. Stopped pedal is `(0, 0)`.
- [ ] **Task 24 — CAN decode.** Synthetic little-endian fields, scale and offset, signed values.
- [ ] **Task 25 — Speed agreement.** Decode then compare within an injected tolerance.
- [ ] **Task 26 — Readout text.** Torque, speed, power, state. Power from the sample property.
- [ ] **Task 27 — Operator session.** Start and stop delegate to `TestRun`.
- [ ] **Task 28 — Window.** Thin tkinter shell. Reviewer opens it.
- [ ] **Task 29 — Heartbeat.** Expired heartbeat returns the safe command. No `sleep`.
- [ ] **Task 30 — Calibration record.** Text record, `not signed`, residual method sentence. Owen and Alex comment before the issue closes.
- [ ] **Task 31 — Shop test.** Blocked until sign-off. No battery connection as a software experiment.

## Spec coverage

| Requirement | Tasks |
| --- | --- |
| R1 Torque | 2, 6, 7, 9, 30 |
| R2 Speed | 20, 24, 25 |
| R3 Power | 1, 10, 26 |
| R4 Strain | 7, 8, 9 |
| R5 Valve | 19, 22 |
| R6 Motor command | 18, 23 |
| R7 CAN | 5, 24, 25 |
| R8 Recording | 4, 11, 12 |
| R9 Import and review | 12, 13, 15, 16 |
| R10 Operator interface | 26, 27, 28 |
| R11 Fail-safe | 18, 29, 31 |
| R12 Calibration traceability | 7, 8, 30 |
| R13 Compact rig | Mechanical, confirmed in task 5 and task 31. No software task pretends to meet it. |

## Self-review

- The chain-drive sentence in the proposal is superseded by the direct-shaft note. Task 5 asks Mechanical to confirm.
- Torque-from-load-cell and torque-from-strain-gauge are both in the proposal. Task 9 keeps one conversion function and does not decide they are the same sensor. Task 5 asks Owen and Alex.
- TBC accuracy, pedal volts, valve tolerance, and CAN layout are arguments or open questions, not constants.
- The shop task cannot start from a green unit test alone.
- Task 17 stores `safe_valve_setpoint` so task 18 does not rename the constructor.

## Execution

The student team implements the GitHub issues and reports every week on the issue. An agent implementation of a single issue, if requested later, should take that issue's tests as the spec and follow TDD.
