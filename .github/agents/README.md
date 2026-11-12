# Agent contracts (provider-agnostic)

Rules live in [`AGENTS.md`](../../AGENTS.md). Prompts live here. **GitHub Actions owns the gates** (CI wait, `lola-review` check, draft-PR expectations). **Which model runs the prompt** is selected by the repo variable `AGENT_PROVIDER`.

| `AGENT_PROVIDER` | Coding agent (`agent-now` / overnight) | Lola |
| --- | --- | --- |
| `cursor` (default) | Cursor / Grokbot automation reads the prompt and opens the draft PR | Automation posts a PR **comment** review; Actions waits for `Lola-Verdict:` |
| `grok` | Same hand-off as `cursor` (Grokbot / Cursor with a Grok model) | Same verdict-comment contract |
| `claude` | `anthropics/claude-code-action` in Actions | Claude runs the review inside Actions |

Switch:

```powershell
gh variable set AGENT_PROVIDER --body cursor   # or grok, or claude
```

## Machine contract for Lola

Whatever provider writes the review must:

1. Follow [prompts/lola-review.md](prompts/lola-review.md) and `AGENTS.md`.
2. Post **one** PR review **comment** (not approve / request-changes).
3. Include a line exactly like:
   - `Lola-Verdict: PASS` or
   - `Lola-Verdict: CHANGES`
4. Never merge.

Actions then labels `review:pass` / `review:changes` and fails the `lola-review` check on CHANGES.

## Machine contract for coding agents

Follow [prompts/coding-agent.md](prompts/coding-agent.md) or [prompts/overnight-agent.md](prompts/overnight-agent.md): one draft PR, `overnight-agent` label, red→green evidence, no workflow edits, `needs-human` if stuck.
