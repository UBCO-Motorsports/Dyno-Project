# Setup: CI, Lola, and overnight coding agents

About 30 minutes. **Rules and prompts are provider-agnostic.** GitHub Actions owns CI and the `lola-review` gate; which AI runs the prompt is a switch.

## How it works

```
 you label an issue          nightly picks one
   "agent-now"                 "overnight-queue" issue
        \                          /
         v                        v
   CODING AGENT (provider: cursor | grok | claude)
   reads AGENTS.md + .github/agents/prompts/* -> DRAFT PR
                              |
            +-----------------+------------------+
            v                                    v
   CI (tests.yml)                        LOLA gate (lola-review.yml)
   ruff, pytest, guardrails              wait for green CI, then provider review
                                         -> Lola-Verdict: PASS|CHANGES
                                         -> check "lola-review"
            \                                    /
             v                                  v
        YOU merge in the morning
```

| File | Purpose |
| --- | --- |
| [`AGENTS.md`](../AGENTS.md) | Rules every provider must follow |
| [`.github/agents/`](../.github/agents/) | Shared prompts + provider switch docs |
| [`.github/workflows/lola-review.yml`](../.github/workflows/lola-review.yml) | Lola gate (provider-agnostic) |
| [`.github/workflows/agent.yml`](../.github/workflows/agent.yml) | `agent-now` coding agent |
| [`.github/workflows/overnight-agent.yml`](../.github/workflows/overnight-agent.yml) | Nightly one-issue pick |
| [`scripts/ci-local.ps1`](../scripts/ci-local.ps1) | Same steps as CI on your machine |

## Switch AI provider

```powershell
gh variable set AGENT_PROVIDER --body cursor   # Grokbot / Cursor (default)
gh variable set AGENT_PROVIDER --body grok     # same hand-off contract as cursor
gh variable set AGENT_PROVIDER --body claude   # Claude Code Action inside GitHub Actions
```

| Value | What runs the model |
| --- | --- |
| `cursor` / `grok` | Your Grokbot / Cursor Automation. Actions posts a hand-off comment and (for Lola) waits for `Lola-Verdict:` |
| `claude` | `anthropics/claude-code-action` in Actions (needs `CLAUDE_CODE_OAUTH_TOKEN`) |

Prompts stay the same either way: `.github/agents/prompts/*.md`.

**Lola contract (every provider):** one comment review + a line `Lola-Verdict: PASS` or `Lola-Verdict: CHANGES`. Never approve / request-changes.

## Ask Grok to work now

| Method | How |
| --- | --- |
| **Actions button** | [Coding agent workflow](https://github.com/UBCO-Motorsports/Dyno-Project/actions/workflows/agent.yml) → **Run workflow** → issue number |
| **Comment** | On the issue, post `/grok` or `/grok now` (OWNER/MEMBER/COLLABORATOR) |
| **Label** | Add `agent-now` |
| **CLI** | `gh workflow run "Coding agent" -f issue_number=10` |

That posts the hand-off comment (cursor/grok) or runs Claude in Actions. Your Grokbot/Cursor automation should watch for comments containing `grok-work-now` or the hand-off heading.

## Labels

| Label | On | Meaning |
| --- | --- | --- |
| `overnight-queue` | issue | Nightly may pick this; does **not** start a run by itself |
| `agent-now` | issue | Start / hand off the coding agent immediately |
| `needs-human` | issue | Agent stopped; a person must answer |
| `overnight-agent` | PR | Opened by a coding agent |
| `review:pass` / `review:changes` | PR | Lola's last verdict |

## Step 1. Variables (all providers)

```powershell
gh variable set AGENT_PROVIDER --body cursor
gh variable set ENABLE_LOLA --body false
gh variable set ENABLE_OVERNIGHT_AGENT --body false
```

## Step 2. Secrets

**Always useful:** fine-grained `GH_PAT` (Contents, Pull requests, Issues = read/write) so agent pushes retrigger CI/Lola:

```powershell
gh secret set GH_PAT
```

**Only if `AGENT_PROVIDER=claude`:**

```powershell
claude setup-token
gh secret set CLAUDE_CODE_OAUTH_TOKEN
```

Install the Claude GitHub App only for the Claude path. Close any PR that adds a stock `claude.yml`.

**If you use Grokbot / Cursor:** no Claude secret required. Point your automation at `.github/agents/prompts/` and `AGENTS.md`. For Lola, trigger after CI is green and post the `Lola-Verdict:` line.

## Step 3. Repository settings

- **Actions → General → Workflow permissions:** Read and write.
- **Rules → `main`:** require `tests (3.11)`, `tests (3.14)`, and `lola-review`.
- `lola-review` always reports: when `ENABLE_LOLA` is false it exits success without reviewing.

## Step 4. Smoke test

1. Keep `ENABLE_LOLA=false` until your provider can post `Lola-Verdict:`.
2. `gh issue edit <n> --add-label agent-now` → hand-off comment (cursor/grok) or Claude draft PR.
3. Open/confirm a draft PR; wait for `tests`.
4. Set `ENABLE_LOLA=true`. On the next push, Lola waits for CI then for your provider’s verdict (or runs Claude).
5. Then `gh variable set ENABLE_OVERNIGHT_AGENT --body true` if you want nightly.

## Local parity

```powershell
.\scripts\ci-local.ps1
```

## Cursor / Grokbot automation tips

- **Coding:** on `agent-now` or the overnight hand-off comment, run `.github/agents/prompts/coding-agent.md` / `overnight-agent.md`.
- **Lola:** on CI success for a PR, run `.github/agents/prompts/lola-review.md` and end with `Lola-Verdict: PASS` or `CHANGES`.
- Do not run Cursor and Claude against the same issue at once.
