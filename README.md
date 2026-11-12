# Dyno software

Laptop-side software for the UBCO Motorsports water-brake dynamometer. The rig measures motor torque and speed, computes power, records each run, and plays repeatable load and pedal profiles. A small real-time controller, not this laptop program, is what keeps the rig safe if the laptop stalls or crashes.

The GitHub issues are the work queue. They are ordered so a new member can finish a task in about an hour, then take longer tasks as the fundamentals get familiar.

**New here?** Read [docs/README.md](docs/README.md) first. It explains the project and every term used below in plain words, and walks through a first issue.

## Deadline and plan

The project ends on **Monday 11 January 2027**. The full schedule is in [docs/delivery-plan.md](docs/delivery-plan.md).

| Date | What |
| --- | --- |
| Thu 26 Nov 2026 | **MVP:** one calibrated, logged, low-load run, with the valve set by hand, that the team can stop at any time |
| Thu 3 Dec 2026 | **Validation:** the rig's numbers checked against independent references |
| 4 Dec – 3 Jan | Exams and break. No deadlines |
| Mon 11 Jan 2027 | **Project ends.** Handover merged |

Sprints are one week and end with a Thursday review in front of the people named for that week. GitHub milestones `S1` to `S6` carry the due dates.

## Start here

**As of 11 Nov 2026:** S1 laptop coding is on `main` (power, torque, limits, log columns, bad inputs, sample, CI). You are in **S2** (review Thu 12 Nov). Full schedule: [docs/delivery-plan.md](docs/delivery-plan.md).

### Late from S1 (people, not code)

| Issue | What you do | Size |
| --- | --- | --- |
| [#5](https://github.com/UBCO-Motorsports/Dyno-Project/issues/5) | Get answers from Owen, Alex, and the sub-teams into `docs/open-questions.md` | 1 hour of messages |
| [#37](https://github.com/UBCO-Motorsports/Dyno-Project/issues/37) | Compare controller boards for Electrical to choose | 2 hours |

### S2 coding (pick from the overnight queue)

| Issue | What you do | Size |
| --- | --- | --- |
| [#7](https://github.com/UBCO-Motorsports/Dyno-Project/issues/7) | Fit a calibration line through synthetic points | half day |
| [#9](https://github.com/UBCO-Motorsports/Dyno-Project/issues/9) | Apply a calibration to a raw bridge reading | half day |
| [#11](https://github.com/UBCO-Motorsports/Dyno-Project/issues/11) | Write a timestamped CSV log | half day |
| [#23](https://github.com/UBCO-Motorsports/Dyno-Project/issues/23) | Clamp pedal voltages and return them to zero | 2 hours |
| [#26](https://github.com/UBCO-Motorsports/Dyno-Project/issues/26) | Format live torque, speed, and power text | 2 hours |

Ask Grok to implement one: label `agent-now`, comment `/grok now`, or [Run Coding agent](https://github.com/UBCO-Motorsports/Dyno-Project/actions/workflows/agent.yml). Queue order: [docs/overnight-queue.md](docs/overnight-queue.md).

## Kanban

Columns are labels. When you start an issue, remove its current `board:` label and add `board: in progress`. When the pull request is waiting on a reviewer, use `board: in review`. Closing the issue moves it to Done. If you are waiting on Owen, Alex, Electrical, Mechanical, or a safety sign-off, use `board: blocked`.

| Column | Open it |
| --- | --- |
| Ready now | [one-hour tasks](https://github.com/UBCO-Motorsports/Dyno-Project/issues?q=is%3Aopen+label%3A%22board%3A+ready+now%22) |
| Up next | [next difficulty](https://github.com/UBCO-Motorsports/Dyno-Project/issues?q=is%3Aopen+label%3A%22board%3A+up+next%22) |
| Later | [larger tasks](https://github.com/UBCO-Motorsports/Dyno-Project/issues?q=is%3Aopen+label%3A%22board%3A+later%22) |
| Blocked on a person | [waiting](https://github.com/UBCO-Motorsports/Dyno-Project/issues?q=is%3Aopen+label%3A%22board%3A+blocked%22) |
| In progress | [being coded](https://github.com/UBCO-Motorsports/Dyno-Project/issues?q=is%3Aopen+label%3A%22board%3A+in+progress%22) |
| In review | [waiting on a reviewer](https://github.com/UBCO-Motorsports/Dyno-Project/issues?q=is%3Aopen+label%3A%22board%3A+in+review%22) |
| Done | [closed issues](https://github.com/UBCO-Motorsports/Dyno-Project/issues?q=is%3Aclosed) |

`board: ready now` is the current sprint, `board: up next` is next week's, and `board: later` is everything after. Within a column, take `difficulty: easy` before `moderate` before `hard`.

Three more labels say why an issue matters:

| Label | Meaning |
| --- | --- |
| `mvp` | Needed for the MVP spin on 26 November. These come first |
| `validation` | Needed for the validation review on 3 December |
| `stretch` | Only after the MVP is accepted. Never start one while an `mvp` issue is at risk |
| `stakeholder feedback` | Someone asked for this at a Thursday review. Goes first in the next sprint |

**Blocked on a person.** [#31](https://github.com/UBCO-Motorsports/Dyno-Project/issues/31) is the first spin and [#47](https://github.com/UBCO-Motorsports/Dyno-Project/issues/47) is validation. They stay here until Mechanical, Electrical, and the safety owners have signed on the issue. Do not spin the motor from a software task.

## What we are building

The team has a Land and Sea water-brake dynamometer. The company no longer exists, and the original control and measurement software is not available. The brake is mechanically usable. Load is set by how much water is in the housing, which a valve controls. The machine under test is the electric motor from EV2, with its motor controller. There is no throttle cable. A pedal signal goes to the vehicle control unit (VCU). The VCU sends a torque command to the motor controller on the vehicle CAN bus.

The primary goal is a working shop rig that:

- measures torque and speed
- calculates mechanical power from those two measurements
- records a CSV file per run
- plays automated holds, sweeps, and lap replays from a procedure CSV
- shows live torque, speed, and power to the operator
- returns the motor command to zero on stop or fault, including when the laptop program fails

Supporting goals from the proposal:

- reuse the existing dynamometer housing
- replace the lost control and measurement software
- make loading automated and repeatable
- keep measurements calibrated, with a written uncertainty
- keep a safe state available without relying on the laptop

This repository is the supervisory software and the tested models behind it: the maths, the file formats, the run state machine, and the operator readouts. From S3 it also holds the controller firmware under `firmware/` ([#42](https://github.com/UBCO-Motorsports/Dyno-Project/issues/42)). The board is chosen by Electrical on 5 November ([#37](https://github.com/UBCO-Motorsports/Dyno-Project/issues/37)).

## How the rig is split

| Block | What it does | Where the work lives |
| --- | --- | --- |
| Mechanical | Water brake, shaft coupling, reaction arm, load cell or strain sensor | Mechanical sub-team. Software does not design the mount. |
| Sensing | Torque, strain, and motor speed | Calibration and unit conversion in this repo. Sensor choice with Owen and Alex. Speed from the VCU, with Electrical. |
| Real-time control | Fixed-time sampling, valve drive, motor command, safe state on a fault | A dedicated controller. This repo specifies the safe behaviour and tests it with fakes. |
| Supervisory station | The laptop: live readouts, logging, procedure playback, high-level setpoints | This repository. |

The laptop is allowed to be slow or to crash. Holding a valve and removing motor torque on a fault must not depend on it. The hardware emergency stop, guarding, and high-voltage isolation are signed off by Mechanical and Electrical. Software supports that setup and does not replace it.

## What "done" means

The project is successful when the team can:

1. Mount the motor on the existing dynamometer and run a controlled shop test.
2. Read calibrated torque and speed live, with power calculated from them.
3. Read the strain channel.
4. Run automated sweeps, holds, and lap replays, and drive the motor through simulated pedal voltages to the VCU.
5. Set the brake load with the valve and command the motor through its controller.
6. Stop safely at any time, including if the laptop software fails.
7. Open, store, and review CSV logs, and load a procedure CSV to run a test.
8. Quote a documented measurement uncertainty when a result is used to validate a motor or hardware change.

Item 1 and any spinning test stay blocked until the safety sign-off issue is cleared. Everything before that is laptop work with fakes and the simulator.

By 11 January the project delivers items 1, 2, 5 (valve set by hand), 6, 7 (logs), and 8, at low load. Item 3 follows once Owen and Alex say whether strain is a separate sensor. Item 4 (automated sweeps, holds, and lap replays) and loading the procedure CSV are stretch work, handed over to next term if unfinished.

## Facts we are building on

These came from the proposal and the notes already written on it.

| Fact | Value |
| --- | --- |
| Peak torque | 150 N·m |
| Maximum speed | 7000 rpm |
| Power cap | below 80 kW |
| Coupling | direct shaft (confirm with Mechanical) |
| Energy source | vehicle tractive battery |
| Strain sample rate | at least 10 Hz |
| Log rate | the slowest of the inputs; speed follows the VCU rate |
| Load profiles | automated sweeps, holds, and lap replays |

Power, in kilowatts:

```text
P (kW) = T (N·m) × speed (rpm) × 2π / 60,000
```

A check you can do on a calculator: 10 N·m at 1000 rpm is about 1.047 kW. Torque is force times arm length, `T = F × r`, with force in newtons and arm length in metres.

150 N·m at 7000 rpm is about 110 kW, which is above the 80 kW cap. The power function reports that true value. A separate check flags the cap. Clipping the number would hide an overload.

Numbers still marked TBC in the proposal stay as arguments to functions. Tests pass an obvious stand-in and name it as an example. The real pedal voltages, arm length, valve units, CAN scaling, and accuracy targets go in `docs/open-questions.md` after the named person answers.

## Who to speak to

| When | Who | Why |
| --- | --- | --- |
| Sensor choice, arm length, strain units, accuracy, calibration sign-off | Owen and Alex | Torque and strain only become validation data after they agree |
| Pedal voltages, CAN definitions, VCU speed rate, tractive battery | Electrical, and whoever holds the message definitions | Do not invent message IDs or voltage limits |
| Coupling, reaction arm, safe valve position, valve tolerance, guarding | Mechanical | The original write-up said "chain drive"; the later note says a direct shaft |
| Emergency stop and high-voltage isolation | The Mechanical and Electrical members who sign safety | Required before any spinning test |
| Sample procedure CSV | Project lead | The schema is already specified; a real file may adjust it |
| Every code change | A teammate who did not write it | That person runs the tests. This is the review gate |

Each issue repeats the rows that apply to that task, split into "before you start" and "before this is used on the rig". An hour-long task does not wait on a sub-team. A shop test does.

## How the work is organised

Epics, in the order a new member should meet them:

1. **Foundations.** Power, torque, named limits, the log columns, and the question list.
2. **Measurement.** Reject impossible numbers, calibrate, uncertainty, strain, one sample record.
3. **Logs.** Write, read, summarise, and reject bad CSV files.
4. **Profiles.** Load a procedure and sample it for holds, sweeps, and replays.
5. **Runner.** The state machine, safe commands, and playback on fakes.
6. **Hardware boundary.** Interfaces, valve tolerance, pedal limits.
7. **CAN.** Decode bytes from a table. Real IDs come from Electrical.
8. **Operator screen.** Text readouts, start/stop, then a small window.
9. **Safety and the shop.** Heartbeat loss, a calibration record someone can sign, then the gated shop test.

Difficulty on every issue:

| Label | What to expect |
| --- | --- |
| Easy · 1 hour | One function or one fixed list. Written so it can be picked up during midterms. |
| Easy · 2 hours | The same kind of work, plus rejected inputs. |
| Moderate · half day | A small module: files, calibration, or a state machine with a full transition list. |
| Hard · multi-day | Several cooperating pieces, still tested without the rig. |
| Expert · gated | Shop validation. Blocked until the named people sign. |

Computer science practice is part of the task, not a side note. The early issues are pure functions and units. Later issues add data invariants, parsers, finite state machines, interfaces with fakes, binary representations, and the split between a slow supervisor and a fast controller.

## Test-driven development

Every coding issue is red, then green.

1. Create a branch from `main`: `issue-<number>-short-name`.
2. Add the test from the issue. Do not add the function body yet.
3. Run the test. It must fail because the behaviour is missing. Paste that failure into the pull request.
4. Write the smallest implementation that matches the formula or rule in the issue.
5. Run `py -m pytest`. Paste the pass into the pull request.
6. Open the pull request. The template asks for both outputs.

Use two commits when you can: `test: ...` then `feat: ...`. One commit is acceptable during a midterm week if both outputs are in the pull request.

A passing test you wrote after the code does not count. The failure first is how we know the test can catch a wrong formula.

### Review gate

The author does not merge their own pull request.

The reviewer:

1. Checks out the branch.
2. Runs `py -m pytest` and reads the new tests, not only the summary line.
3. Confirms units in the names, and that TBC limits were not replaced with an invented "real" value.
4. Comments on the pull request with the pytest result.
5. Merges only if the acceptance list in the issue is met.

If the issue names a person to consult before hardware use, merging the laptop code does not close that gate. Comment on the issue with the date, the name, and what they confirmed. Leave the card in **Blocked on a person** until that comment exists.

### Weekly report

Every member posts one comment on the pinned thread [#35](https://github.com/UBCO-Motorsports/Dyno-Project/issues/35) before Sunday night, including midterm weeks, and including weeks where the only honest update is that the task was not started. The template is in that issue. Its last line asks whether your issue will make its Thursday review: **yes**, **at risk**, or **no**. Saying "at risk" on Sunday is how the team gets time to help.

## Repository map

Code lives under `src/dyno/`. Tests live under `tests/`. New modules are added by the issues, one responsibility each:

| Module | Responsibility | Issue introduces it |
| --- | --- | --- |
| `power.py` | `mechanical_power_kw(torque_nm, speed_rpm) -> float` | Power |
| `torque.py` | `torque_nm(force_n, arm_length_m) -> float` | Torque |
| `limits.py` | 150 N·m, 7000 rpm, 80 kW cap, 10 Hz strain floor | Limits |
| `log_schema.py` | `LOG_COLUMNS` | Log columns |
| `calibration.py` | Least-squares fit through three or more points, apply, residuals, signed record | Calibration issues |
| `sample.py` | One timestamped `Sample`, power from torque and speed | Sample record |
| `log_csv.py` | Write, read, summarise, reject a bad log | Log issues |
| `profile.py` | Procedure CSV and interpolation | Profile issues |
| `run_state.py` | `TestRun`, `RunState`, `RunEvent`, `RigCommand` | State machine |
| `runner.py` | Play a profile on fake outputs | Playback |
| `timing.py` | `log_rate_hz(...)` | Sample rate |
| `ports.py` | Sensor and actuator interfaces | Ports |
| `valve.py` | `within_tolerance(commanded, achieved, tolerance)` | Valve |
| `pedal.py` | `PedalLimits`, `clamp_pedal`, `stopped_pedal` | Pedal |
| `can_decode.py` | `SignalDef`, `decode_signal` | CAN |
| `readout.py` | Operator text and start/stop | Readout |
| `operator_app.py` | Window over the readout | Window |
| `watchdog.py` | Heartbeat timeout | Watchdog |
| `rig_config.py` | `RigConfig` read from `rig.toml` | [#38](https://github.com/UBCO-Motorsports/Dyno-Project/issues/38) |
| `link.py` | Laptop–controller messages; cases in `tests/contract/link_cases.json` | [#40](https://github.com/UBCO-Motorsports/Dyno-Project/issues/40) |
| `simulator.py` | Motor and water-brake model behind the ports | [#41](https://github.com/UBCO-Motorsports/Dyno-Project/issues/41) |
| `plot.py` | Torque and power against speed from a CSV | [#44](https://github.com/UBCO-Motorsports/Dyno-Project/issues/44) |
| `run_metadata.py` | `<run>.meta.json` next to each CSV | [#46](https://github.com/UBCO-Motorsports/Dyno-Project/issues/46) |
| `firmware/` | Controller loop, sensors, outputs, watchdog | [#42](https://github.com/UBCO-Motorsports/Dyno-Project/issues/42) |

Shared shapes later issues must keep:

```python
LOG_COLUMNS = (
    "timestamp_utc",
    "torque_nm",
    "speed_rpm",
    "power_kw",
    "strain",
    "valve_setpoint",
    "pedal_voltage_a",
    "pedal_voltage_b",
    "run_state",
)

# procedure CSV header
# time_s,pedal_voltage_a,pedal_voltage_b,load_setpoint
```

`RunState` is `idle`, `armed`, `running`, `safe`. `RunEvent` is `arm`, `start`, `stop`, `fault`, `acknowledge`. Stop and fault move to `safe` and the command becomes zero pedal voltage, zero torque command, and the injected safe valve setpoint. There is no laptop-side ramp. A ramp that delayed torque removal would make safety depend on this program still running.

## Setup

You need Python 3.11 or newer. Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

Every test should pass on a fresh clone of `main`. Do not commit `.venv/`.

## Prior art

These public projects are useful reading. They are not the design, and their code is not copied into this repo.

- [DIY-Dyno](https://github.com/DeeEmm/DIY-Dyno)
- [odrive_based_electric_motor_dynamometer](https://github.com/Capo01/odrive_based_electric_motor_dynamometer)

Our constraints are different: a water brake, a VCU and pedal voltages, the vehicle CAN bus, the tractive battery, and a hard split between the laptop and the real-time controller.

## Safety boundary

Do not spin the motor, connect the tractive battery, or command the valve on the physical rig as part of a software issue. The shop-test issue lists the sign-offs that have to exist first. Unit tests use numbers and fakes only.
