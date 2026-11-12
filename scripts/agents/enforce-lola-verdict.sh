#!/usr/bin/env bash
set -euo pipefail
PR="${1:?PR number}"
v=$(tr -d '[:space:]' < review-verdict.txt 2>/dev/null || echo MISSING)
echo "Lola verdict: $v"
if [ "$v" = "PASS" ]; then
  gh pr edit "$PR" --add-label "review:pass" --remove-label "review:changes" || true
  exit 0
fi
gh pr edit "$PR" --add-label "review:changes" --remove-label "review:pass" || true
echo "::error::Lola review did not pass (verdict: $v). See the review comment."
exit 1
