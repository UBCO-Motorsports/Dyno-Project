# AGENTS.md

Rules for coding agents (overnight, Cursor cloud, Lola) and for humans reviewing their pull requests. Read this before the first write in a session. It overrides generic defaults.

The laptop program in this repo is a supervisor for a water-brake dynamometer. It is not the safety system. Never spin the motor, connect the tractive battery, or drive the physical valve as part of a software task.

---

## Roles

| Role | Job | Must not |
| --- | --- | --- |
| Overnight coding agent | Pick the next `overnight-queue` issue (nightly) or an `agent-now` issue (immediate); implement with TDD; open one **draft** PR labelled `overnight-agent` | Merge, invent hardware numbers, touch blocked or field issues, edit `.github/workflows/` |
| Lola (CI review) | After CI is green on a PR, review the diff against this file and the issue; post one review; set the `lola-review` check to PASS or CHANGES | Merge, rewrite the PR, invent requirements the issue did not state, `--approve` |
| Human reviewer | Run the tests, check the red evidence, approve or request changes | Rubber-stamp green CI as a review |

Live wiring: [`.github/workflows/`](.github/workflows/) and setup steps in [`docs/github-setup.md`](docs/github-setup.md). Lola and nightly stay off until `ENABLE_LOLA` / `ENABLE_OVERNIGHT_AGENT` are `true` and secrets exist.

---

## Overnight agent bucket

### What goes in the bucket

An issue may carry `overnight-queue` only when **all** of these are true:

- It is a coding task (creates or changes Python under `src/dyno/` or `tests/`, or a CI/config file the issue names).
- It is **not** `board: blocked`, **not** `field task`, **not** `difficulty: expert`.
- The issue body already states the behaviour and acceptance; the agent does not need a product decision.
- Hardware values the issue needs are either fixed in the README, or the issue says to use example numbers in tests.

Blocked, gated, or conversation-only work stays out: `#5`, `#31`, `#37`, `#42` (until the board is chosen and on the bench), `#47`, `#48`, `#35`.

The ordered queue lives in [`docs/overnight-queue.md`](docs/overnight-queue.md). Nightly runs (`overnight-agent.yml`, when `ENABLE_OVERNIGHT_AGENT=true`) take issues from the top of that list that still have `overnight-queue` and no open PR closing them. The `agent-now` label starts one run immediately (`agent.yml`); `overnight-queue` alone never starts a run.

### How the overnight agent opens a PR

1. Restate the issue in one short paragraph: what you will change, what you will not change, and which acceptance lines you will prove.
2. Branch from current `main`: `issue-<number>-<short-name>`.
3. **Red first.** Add or extend the tests from the issue. Commit `test: ...`. Run them. They must fail for a real reason (missing symbol, failed assertion). Paste that failure into the PR. A red that says `collected 0 items` or that never imported the new test file does not count.
4. **Green.** Implement the smallest code that matches the issue. Commit `feat: ...` (or `fix: ...`). Run `bash scripts/ci-local.sh` or `.\scripts\ci-local.ps1` (same steps as CI). Never claim a check passed unless you ran it.
5. Open **one draft** PR that closes **one** issue. Fill `.github/pull_request_template.md`. Label the PR `overnight-agent`. Remove `overnight-queue` / `agent-now` from the issue. Do not also label unrelated open PRs.
6. If you cannot finish: comment, add `needs-human`, stop. Never end silently.
7. Stop. Do not merge. Do not start a second issue in the same run unless the queue file says the pair must land together (they almost never do).

### Hard limits for overnight runs

- One issue → one PR → one concern.
- Do not invent CAN ids, pedal voltages, arm lengths, or safe valve positions. If `docs/open-questions.md` has no answer, keep the value as a function argument and use the example from the issue tests.
- Do not edit `docs/open-questions.md` answers, safety sign-off checklists, or firmware wiring as part of a maths or logging issue.
- Do not add dependencies unless the issue names them.
- Do not edit `.github/workflows/`.
- Do not push to `main`. Do not enable auto-merge.
- Use a fine-grained `GH_PAT` for push/PR so CI and Lola still run (see [`docs/github-setup.md`](docs/github-setup.md)).

---

## How a PR must look

Every PR description includes:

| Section | Required content |
| --- | --- |
| Issue | `Closes #<n>` |
| Red evidence | Exact command and failure **before** the implementation existed |
| Green evidence | Exact command and pass **after** |
| Notes | What you did not change that a reviewer might expect; anything unsure |

Title style: `feat(area): …`, `test(area): …`, `fix(area): …`, `ci: …`, or `docs: …`. Prefer squash-merge with that title as the commit.

Two commits when possible (`test:` then `feat:`). One commit is fine if both red and green outputs are in the description.

---

## Lola as an extension of CI

Lola is the automated review step in [`.github/workflows/lola-review.yml`](.github/workflows/lola-review.yml). CI proves the suite is green. Lola proves the change matches the issue and is not tautological. The job posts one review comment and fails the **`lola-review`** status check on CHANGES (labels `review:pass` / `review:changes`). Neither replaces a human merge on `main`.

### When Lola runs

- Trigger: pull request opened / synchronized / reopened / ready for review (same-repo branches only).
- Lola waits for the `tests` checks. If CI failed or timed out: comment with the failing job name, set CHANGES, do not rewrite the branch.
- If CI passed: review the diff against the linked issue and this file, then post a single **comment** review (never `--approve`).

### What Lola checks

1. **Issue link.** The PR closes exactly one issue, and the diff matches that issue's files and signature.
2. **Red is real.** The pasted failure names the new test module or assertion. Reject `collected 0 items` as red evidence.
3. **Acceptance.** Each unchecked acceptance line in the issue is either satisfied by a test in the diff or called out as unmet.
4. **Units and names.** Public names keep units (`torque_nm`, `speed_rpm`, `power_kw`, …).
5. **No invented hardware.** No new literal for arm length, pedal volts, CAN id, or safe valve outside example tests or `rig.example.toml`.
6. **Tautology.** Apply the section below. If a test cannot fail when the behaviour is wrong, request changes.
7. **Scope.** No drive-by refactors, no extra features the issue did not ask for (unless the PR notes them and they are clearly separated). No workflow edits by coding agents.
8. **Safety boundary.** No code that talks to the physical rig, skips the E-stop story, or treats the laptop as the safety system.

### What Lola must not do

- Merge the PR.
- Approve (`gh pr review --approve`) — humans only.
- Approve when CI is red.
- Treat its own follow-up commits as reviewed without a new CI + Lola run.
- Ask for style-only nits (import order, comment taste) when behaviour and tests are sound.
- Demand stakeholder sign-off that the issue deferred until hardware use.

Human reviewers still run `.\scripts\ci-local.ps1` (or trust a CI run they opened themselves) and are the only merge authority.

---

## Tautological code (reject this)

A check is **tautological** when it cannot fail if the behaviour is wrong. Agents produce these by accident. Reviewers and Lola must reject them.

### 1. Expected value copied from the implementation

```python
# BAD: same expression on both sides — a wrong formula in both places still passes
expected = torque_nm * speed_rpm * 2 * math.pi / 60_000
assert mechanical_power_kw(torque_nm, speed_rpm) == expected
```

Prefer at least one of:

- a **hand-computed literal** the README already states (`10 N·m` at `1000 rpm` ≈ `1.047197…`), or
- an **independent derivation** written out in the test comment with intermediate numbers, or
- a property that would fail under a plausible bug (for example `result > 80` for the over-cap case, without recomputing the full formula for that assert).

Recomputing the formula inline is acceptable **only** when the issue prescribed that exact test text; even then, Lola should note it and a human should spot-check one numeric literal against a calculator.

### 2. Tests that only assert the code exists

```python
# BAD
assert callable(mechanical_power_kw)
assert PEAK_TORQUE_NM is not None
```

Constants may be compared to the agreed numbers (`== 150`). Callability alone is not a behaviour test.

### 3. Red evidence that never ran the new test

`collected 0 items`, or a failure from a missing file path you did not add, is not a failing test of the new behaviour. The red run must import the new test module and fail on the missing symbol or assertion.

### 4. Implementation that mirrors a buggy test

If the test encodes the wrong rule and the code is written to satisfy that test, both are wrong together. When the issue and the README disagree, stop and ask; do not "make the test pass" by inventing a third rule.

### 5. Broad `except` or silent defaults

Swallowing `Exception` to return `0`, or catching failures to keep CI green, is tautological safety: the suite stays green while the rig would see a lie. Let bad inputs raise the error the issue names.

### 6. Duplicate sources of truth

Do not hard-code `80` in a caller when `POWER_CAP_KW` exists. Do not re-derive slope inline when `fit_calibration_line` / `apply_calibration` already exist. A second copy will drift and tests on one copy will not protect the other.

### 7. Comments that replace proof

A comment that says "correct by inspection" without a test is not verification. Delete the comment or add the test.

---

## Review manner (humans and Lola)

Order of importance: **correct, safe, holds for one operator laptop, tested, lean.**

For each finding, state: what it is, the concrete bad case, the smallest fix, and what happens if we skip it. Skip empty groups.

- **Must fix:** wrong result, fake red evidence, tautological test, invented hardware constant, safety-boundary breach.
- **Should fix:** missing rejection case the issue asked for, duplicated truth, scope creep.
- **Nice to have:** shorter form that does not change behaviour.

Approve only when Must-fix is empty and CI is green. The author never merges their own PR.

---

## Commands

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\scripts\ci-local.ps1
```

Same checks as GitHub CI (install, ruff, pytest, guardrails). On Ubuntu agents: `bash scripts/ci-local.sh`.

Expected load: one operator on one laptop, plus CI and Lola on each PR. Do not design for multi-tenant servers.

---

## When to stop and ask a human

- The issue needs a product or hardware choice not answered in `docs/open-questions.md`.
- The task is labelled `field task`, `board: blocked`, or `difficulty: expert`.
- Two attempts at the same approach failed.
- Changing branch protection, secrets, or who may merge.

Comment on the issue, add `needs-human`, report what you tried, and stop. Do not loop.
