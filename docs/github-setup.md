# Setup: CI, Lola, and overnight coding agents

About 30 minutes. Agents run on **GitHub Actions** — your laptop does not need to stay on. You only need it once to create tokens and run a smoke test.

## How it works

```
 you label an issue          nightly 2:17 AM picks one
   "agent-now"                 "overnight-queue" issue
        \                          /
         v                        v
   CODING AGENT (agent.yml / overnight-agent.yml)
   reads AGENTS.md + the issue -> branch -> TDD -> DRAFT PR
                              |
            +-----------------+------------------+
            v                                    v
   CI (tests.yml)                        LOLA (lola-review.yml)
   ruff, pytest, guardrails              checks acceptance + AGENTS.md
   -> checks "tests (3.11/3.14)"         -> review comment + check "lola-review"
            \                                    /
             v                                  v
        YOU review in the morning: merge, or fix and push
```

| File | Purpose |
| --- | --- |
| [`AGENTS.md`](../AGENTS.md) | Rules every agent and Lola follow |
| [`.github/workflows/tests.yml`](../.github/workflows/tests.yml) | CI: ruff, pytest, safety guardrails |
| [`.github/workflows/lola-review.yml`](../.github/workflows/lola-review.yml) | Lola: independent review + `lola-review` check |
| [`.github/workflows/agent.yml`](../.github/workflows/agent.yml) | Coding agent on `agent-now` |
| [`.github/workflows/overnight-agent.yml`](../.github/workflows/overnight-agent.yml) | One `overnight-queue` issue per night |
| [`scripts/ci-local.ps1`](../scripts/ci-local.ps1) / [`.sh`](../scripts/ci-local.sh) | Same steps as CI on your machine |

**Labels**

| Label | On | Meaning |
| --- | --- | --- |
| `overnight-queue` | issue | Nightly may pick this; does **not** start a run by itself |
| `agent-now` | issue | Start the coding agent on this issue immediately |
| `needs-human` | issue | Agent stopped; a person must answer |
| `overnight-agent` | PR | Opened by the coding agent |
| `review:pass` / `review:changes` | PR | Lola's last verdict |

## Prerequisites

- A Claude **Pro or Max** plan (agent runs use that plan's usage).
- Claude Code CLI (`claude --version`).
- GitHub CLI logged in: `gh auth login`.

## Step 1. Secrets and variables

**1. Claude token**

```powershell
claude setup-token
gh secret set CLAUDE_CODE_OAUTH_TOKEN
```

**2. Fine-grained `GH_PAT`** (GitHub → Settings → Developer settings → Fine-grained tokens)

- Repository access: only this repo.
- Permissions: Contents, Pull requests, Issues = read and write.
- Expiry: 90 days; calendar reminder to rotate.

```powershell
gh secret set GH_PAT
```

Why: pushes made with the default `GITHUB_TOKEN` do **not** trigger other workflows. Without `GH_PAT`, CI and Lola never run on agent PRs.

**3.** Install the Claude GitHub App on the repo (`/install-github-app` in Claude Code). If it opens a PR adding its own `claude.yml`, close that PR; these workflows replace it.

**4.** Leave Lola and nightly **off** until secrets are in and the smoke test passes:

```powershell
gh variable set ENABLE_LOLA --body false
gh variable set ENABLE_OVERNIGHT_AGENT --body false
```

After the smoke test:

```powershell
gh variable set ENABLE_LOLA --body true
gh variable set ENABLE_OVERNIGHT_AGENT --body true
```

## Step 2. Repository settings

- **Actions → General → Workflow permissions:** Read and write.
- **Rules → branch ruleset for `main`:**
  - Require a pull request.
  - Require status checks `tests (3.11)`, `tests (3.14)`, and `lola-review` (add `lola-review` after its first green run appears in the picker).
  - `lola-review` always reports: when `ENABLE_LOLA` is false it exits success without reviewing, so turning Lola off does not freeze merges. Prefer keeping `ENABLE_LOLA=true` once secrets work.
  - Prefer requiring one human approval when the author is not the only reviewer. Agent PRs opened with your `GH_PAT` count as yours — GitHub will not let you approve your own PR, so either use a bot account for `GH_PAT` or rely on the automated checks plus your merge click.
  - Lola only posts **comment** reviews (never approve / request-changes). The failed `lola-review` check is the gate.

## Step 3. Smoke test

1. Pick a tiny overnight-safe issue (or open a throwaway one).
2. `gh issue edit <n> --add-label agent-now`
3. Wait for the coding agent workflow → draft PR with `overnight-agent`.
4. Confirm `tests` runs, then Lola posts a review and the `lola-review` check is green or red with a useful comment.
5. Only then: `gh variable set ENABLE_LOLA --body true` and `gh variable set ENABLE_OVERNIGHT_AGENT --body true`

## Local parity

```powershell
.\scripts\ci-local.ps1
```

Agents on Ubuntu run `bash scripts/ci-local.sh`.

## Cursor overnight (optional)

You can still run a Cursor cloud/overnight agent that follows `AGENTS.md` by hand. The Actions path above is the unattended GitHub factory; Cursor is fine for interactive work. Do not run both against the same issue at once.
