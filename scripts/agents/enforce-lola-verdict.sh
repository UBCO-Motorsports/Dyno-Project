#!/usr/bin/env bash
# Apply Lola labels and, on PASS, approve as the GH_TOKEN user (PR_ASSIGNEE / GH_PAT).
# Reviews and comments must use GH_PAT so they appear as the human owner, not github-actions.
set -euo pipefail
PR="${1:?PR number}"
v=$(tr -d '[:space:]' < review-verdict.txt 2>/dev/null || echo MISSING)
echo "Lola verdict: $v"
if [ "$v" = "PASS" ]; then
  gh pr edit "$PR" --add-label "review:pass" --remove-label "review:changes" || true
  # Approve as the token owner (KitheK when GH_PAT is set). Fails if the same
  # account authored the PR — GitHub blocks self-approve; that is expected.
  if gh pr review "$PR" --approve --body "Lola-Verdict: PASS — approved by PR owner token."; then
    echo "Approved PR #$PR as $(gh api user --jq .login)"
  else
    echo "::warning::Could not approve PR #$PR (often self-approve blocked). Labels still set; approve in the UI as yourself."
  fi
  exit 0
fi
gh pr edit "$PR" --add-label "review:changes" --remove-label "review:pass" || true
echo "::error::Lola review did not pass (verdict: $v). See the PR conversation comment."
exit 1
