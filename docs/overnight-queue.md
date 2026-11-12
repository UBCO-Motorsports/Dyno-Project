# Overnight agent queue

Ordered list of **non-blocking** coding issues for the overnight agent. Rules: [`AGENTS.md`](../AGENTS.md). Wiring: [`github-setup.md`](github-setup.md).

An issue stays on this list while it has the `overnight-queue` label and there is no open PR that closes it. Nightly (`ENABLE_OVERNIGHT_AGENT=true`) picks **one** row from the top. To run immediately instead, add `agent-now` (or comment `/grok now`). When a PR opens, remove `overnight-queue` / `agent-now` from the issue and put `overnight-agent` on the **draft** PR. When the PR merges, the row is done. If the agent is stuck, it adds `needs-human`.

Skipped on purpose (not overnight work): field / stakeholder conversations (`#5`, `#37`), blocked shop work (`#31`, `#47`), firmware until the board is chosen (`#42`), stretch items, weekly reports (`#35`), handover writing (`#48`).

## Done recently (on `main`)

| Issue | PR | Module |
| --- | ---: | --- |
| [#1](https://github.com/UBCO-Motorsports/Dyno-Project/issues/1) Power | [#32](https://github.com/UBCO-Motorsports/Dyno-Project/pull/32) | `power.py` |
| [#2](https://github.com/UBCO-Motorsports/Dyno-Project/issues/2) Torque | [#33](https://github.com/UBCO-Motorsports/Dyno-Project/pull/33) | `torque.py` |
| [#3](https://github.com/UBCO-Motorsports/Dyno-Project/issues/3) Limits | [#52](https://github.com/UBCO-Motorsports/Dyno-Project/pull/52) | `limits.py` |
| [#4](https://github.com/UBCO-Motorsports/Dyno-Project/issues/4) Log columns | [#34](https://github.com/UBCO-Motorsports/Dyno-Project/pull/34) | `log_schema.py` |
| [#6](https://github.com/UBCO-Motorsports/Dyno-Project/issues/6) Reject bad inputs | [#53](https://github.com/UBCO-Motorsports/Dyno-Project/pull/53) | `power.py` / `torque.py` |
| [#10](https://github.com/UBCO-Motorsports/Dyno-Project/issues/10) Sample record | [#60](https://github.com/UBCO-Motorsports/Dyno-Project/pull/60) | `sample.py` |
| [#36](https://github.com/UBCO-Motorsports/Dyno-Project/issues/36) CI | [#54](https://github.com/UBCO-Motorsports/Dyno-Project/pull/54) | `.github/workflows/tests.yml` |

## Now (open PRs already in the overnight-agent bucket)

| PR | Issue | Notes |
| --- | --- | --- |
| _(none)_ | — | Queue is clear after [#60](https://github.com/UBCO-Motorsports/Dyno-Project/pull/60) |

## Next issues to open as PRs (top first)

| Order | Issue | Why it is overnight-safe |
| --- | ---: | --- |
| 1 | [#7](https://github.com/UBCO-Motorsports/Dyno-Project/issues/7) | Calibration fit; tests use synthetic points |
| 2 | [#9](https://github.com/UBCO-Motorsports/Dyno-Project/issues/9) | Apply calibration; no hardware |
| 3 | [#8](https://github.com/UBCO-Motorsports/Dyno-Project/issues/8) | Residuals; depends on #7/#9 maths only |
| 4 | [#11](https://github.com/UBCO-Motorsports/Dyno-Project/issues/11) | Write CSV; Sample (#10) is on main |
| 5 | [#23](https://github.com/UBCO-Motorsports/Dyno-Project/issues/23) | Pedal clamp; example limits in tests |
| 6 | [#26](https://github.com/UBCO-Motorsports/Dyno-Project/issues/26) | Readout text; needs Sample |
| 7 | [#17](https://github.com/UBCO-Motorsports/Dyno-Project/issues/17) | State machine; pure logic |
| 8 | [#21](https://github.com/UBCO-Motorsports/Dyno-Project/issues/21) | Ports + fakes; unblocks simulator |
| 9 | [#38](https://github.com/UBCO-Motorsports/Dyno-Project/issues/38) | Rig config; example TOML only |
| 10 | [#39](https://github.com/UBCO-Motorsports/Dyno-Project/issues/39) | Pedal pair; needs #23 |
| 11 | [#12](https://github.com/UBCO-Motorsports/Dyno-Project/issues/12) | Read CSV; needs #11 |
| 12 | [#18](https://github.com/UBCO-Motorsports/Dyno-Project/issues/18) | Safe command; needs #17 |
| 13 | [#27](https://github.com/UBCO-Motorsports/Dyno-Project/issues/27) | Operator session; needs #26/#18 |
| 14 | [#29](https://github.com/UBCO-Motorsports/Dyno-Project/issues/29) | Heartbeat model; laptop side only |
| 15 | [#44](https://github.com/UBCO-Motorsports/Dyno-Project/issues/44) | Plot a run; needs #12 |
| 16 | [#43](https://github.com/UBCO-Motorsports/Dyno-Project/issues/43) | Manual controls; needs #27/#39 |
| 17 | [#41](https://github.com/UBCO-Motorsports/Dyno-Project/issues/41) | Simulator; needs #21 |
| 18 | [#40](https://github.com/UBCO-Motorsports/Dyno-Project/issues/40) | Link messages; shared JSON cases |
| 19 | [#45](https://github.com/UBCO-Motorsports/Dyno-Project/issues/45) | End-to-end on simulator; needs several above |
| 20 | [#28](https://github.com/UBCO-Motorsports/Dyno-Project/issues/28) | Operator window; needs #27 |
| 21 | [#30](https://github.com/UBCO-Motorsports/Dyno-Project/issues/30) | Calibration record formatter (code); sign-off stays human |
| 22 | [#13](https://github.com/UBCO-Motorsports/Dyno-Project/issues/13) | Log summary; validation path |
| 23 | [#46](https://github.com/UBCO-Motorsports/Dyno-Project/issues/46) | Run metadata; needs #11/#38/#30 |

One overnight run should take **one** row from "Next", following dependencies if a higher row is still open.
