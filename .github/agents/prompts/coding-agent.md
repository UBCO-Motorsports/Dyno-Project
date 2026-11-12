# Coding agent prompt (`agent-now`)

Implement GitHub issue `$ISSUE` in `$REPO`.

1. Read `AGENTS.md`, then the issue (`gh issue view $ISSUE --comments`).
   Skim `docs/overnight-queue.md` and `docs/open-questions.md` if hardware numbers appear.
2. If labeled `needs-human`, `board: blocked`, `field task`, or `difficulty: expert`, or criteria are ambiguous:
   comment with questions, add `needs-human`, remove `agent-now`, stop. Do not invent hardware numbers.
3. Restate on the issue: what you will change, what you will not, which acceptance lines you will prove.
4. Branch `issue-$ISSUE-<short-name>` from current `main`.
   **Red first:** tests from the issue; commit `test: ...`; they must fail for a real reason; capture output.
   **Green:** smallest code that matches; commit `feat: ...` or `fix: ...`.
5. Before pushing, run `bash scripts/ci-local.sh` or `.\scripts\ci-local.ps1` until it passes.
6. Open a **DRAFT** PR from `.github/pull_request_template.md`: `Closes #$ISSUE`, red evidence, green evidence, notes.
   Label the PR `overnight-agent`. Lola will review it.
7. Comment on the issue with the PR link. Remove `agent-now` and `overnight-queue` from the issue.

Never push to `main`, never merge, never edit `.github/workflows/`, never enable auto-merge,
never add dependencies unless the issue names them, never treat the laptop as the safety system,
never spin the motor / connect the tractive battery / drive the physical valve.
If blocked: comment, add `needs-human`, stop.
