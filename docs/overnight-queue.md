# Overnight agent queue

Ordered list of **non-blocking** coding issues for the overnight agent. Rules: [`AGENTS.md`](../AGENTS.md).

An issue stays on this list while it has the `overnight-queue` label and there is no open PR that closes it. When a PR opens, remove `overnight-queue` from the issue and put `overnight-agent` on the PR. When the PR merges, the row is done.

Skipped on purpose (not overnight work): field / stakeholder conversations (`#5`, `#37`), blocked shop work (`#31`, `#47`), firmware until the board is chosen (`#42`), stretch items, weekly reports (`#35`), handover writing (`#48`).

## Now (open PRs already in the overnight-agent bucket)

| PR | Issue | Notes |
| --- | --- | --- |
| _(none)_ | — | #54 CI, #53 reject bad inputs, and #51 delivery plan are on `main` |

## Next issues to open as PRs (top first)

| Order | Issue | Why it is overnight-safe |
| --- | ---: | --- |
| 1 | [#10](https://github.com/UBCO-Motorsports/Dyno-Project/issues/10) | Sample record; synthetic data; unblocks CSV |
| 2 | [#7](https://github.com/UBCO-Motorsports/Dyno-Project/issues/7) | Calibration fit; tests use synthetic points |
| 3 | [#9](https://github.com/UBCO-Motorsports/Dyno-Project/issues/9) | Apply calibration; no hardware |
| 4 | [#8](https://github.com/UBCO-Motorsports/Dyno-Project/issues/8) | Residuals; depends on #7/#9 maths only |
| 5 | [#11](https://github.com/UBCO-Motorsports/Dyno-Project/issues/11) | Write CSV; needs #10 |
| 6 | [#23](https://github.com/UBCO-Motorsports/Dyno-Project/issues/23) | Pedal clamp; example limits in tests |
| 7 | [#26](https://github.com/UBCO-Motorsports/Dyno-Project/issues/26) | Readout text; needs Sample |
| 8 | [#17](https://github.com/UBCO-Motorsports/Dyno-Project/issues/17) | State machine; pure logic |
| 9 | [#21](https://github.com/UBCO-Motorsports/Dyno-Project/issues/21) | Ports + fakes; unblocks simulator |
| 10 | [#38](https://github.com/UBCO-Motorsports/Dyno-Project/issues/38) | Rig config; example TOML only |
| 11 | [#39](https://github.com/UBCO-Motorsports/Dyno-Project/issues/39) | Pedal pair; needs #23 |
| 12 | [#12](https://github.com/UBCO-Motorsports/Dyno-Project/issues/12) | Read CSV; needs #11 |
| 13 | [#18](https://github.com/UBCO-Motorsports/Dyno-Project/issues/18) | Safe command; needs #17 |
| 14 | [#27](https://github.com/UBCO-Motorsports/Dyno-Project/issues/27) | Operator session; needs #26/#18 |
| 15 | [#29](https://github.com/UBCO-Motorsports/Dyno-Project/issues/29) | Heartbeat model; laptop side only |
| 16 | [#44](https://github.com/UBCO-Motorsports/Dyno-Project/issues/44) | Plot a run; needs #12 |
| 17 | [#43](https://github.com/UBCO-Motorsports/Dyno-Project/issues/43) | Manual controls; needs #27/#39 |
| 18 | [#41](https://github.com/UBCO-Motorsports/Dyno-Project/issues/41) | Simulator; needs #21 |
| 19 | [#40](https://github.com/UBCO-Motorsports/Dyno-Project/issues/40) | Link messages; shared JSON cases |
| 20 | [#45](https://github.com/UBCO-Motorsports/Dyno-Project/issues/45) | End-to-end on simulator; needs several above |
| 21 | [#28](https://github.com/UBCO-Motorsports/Dyno-Project/issues/28) | Operator window; needs #27 |
| 22 | [#30](https://github.com/UBCO-Motorsports/Dyno-Project/issues/30) | Calibration record formatter (code); sign-off stays human |
| 23 | [#13](https://github.com/UBCO-Motorsports/Dyno-Project/issues/13) | Log summary; validation path |
| 24 | [#46](https://github.com/UBCO-Motorsports/Dyno-Project/issues/46) | Run metadata; needs #11/#38/#30 |

One overnight run should take **one** row from "Next", following dependencies if a higher row is still open.
