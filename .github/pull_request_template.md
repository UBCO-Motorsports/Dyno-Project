## Issue

Closes #

Agents: follow root `AGENTS.md` (TDD red→green, no invented hardware, no tautological tests). Overnight / `agent-now` PRs are **draft**, take the `overnight-agent` label, and must not edit `.github/workflows/`. Setup: `docs/github-setup.md`.

## Test evidence

Paste the command and the failure from before the implementation (must name the new test; `collected 0 items` does not count):

```
```

Paste the command and the pass from after the implementation:

```
```

## Review

- [ ] A different person checked out this branch and ran `.\scripts\ci-local.ps1` (or inspected a CI run they opened)
- [ ] The tests check the behaviour in the issue, including at least one rejected input where the issue asks for it
- [ ] Names and units match the issue (`torque_nm`, `speed_rpm`, `power_kw`)
- [ ] Tests are not tautological (see `AGENTS.md`: expected value not a copy of the implementation with no independent check)
- [ ] Any stakeholder note required by the issue is commented on the issue
- [ ] Lola `lola-review` check has run after green `tests` (PASS or addressed CHANGES)

## Weekly report

If the week is ending, post on the pinned weekly thread (#35) and name this issue.
