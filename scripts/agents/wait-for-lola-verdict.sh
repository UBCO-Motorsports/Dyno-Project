#!/usr/bin/env bash
# Wait for a PR comment/review body containing "Lola-Verdict: PASS|CHANGES".
# Writes review-verdict.txt (PASS or CHANGES). Used when AGENT_PROVIDER is cursor|grok.
set -euo pipefail
PR="${1:?PR number}"
# ~25 minutes
for i in $(seq 1 75); do
  body=$(gh api "repos/${GITHUB_REPOSITORY}/pulls/${PR}/comments" --paginate --jq '.[].body' 2>/dev/null || true)
  body+=$'\n'
  body+=$(gh api "repos/${GITHUB_REPOSITORY}/issues/${PR}/comments" --paginate --jq '.[].body' 2>/dev/null || true)
  body+=$'\n'
  body+=$(gh api "repos/${GITHUB_REPOSITORY}/pulls/${PR}/reviews" --paginate --jq '.[].body' 2>/dev/null || true)
  if printf '%s' "$body" | grep -Eq 'Lola-Verdict:[[:space:]]*PASS'; then
    echo PASS > review-verdict.txt
    echo "Found Lola-Verdict: PASS"
    exit 0
  fi
  if printf '%s' "$body" | grep -Eq 'Lola-Verdict:[[:space:]]*CHANGES'; then
    echo CHANGES > review-verdict.txt
    echo "Found Lola-Verdict: CHANGES"
    exit 0
  fi
  echo "poll $i: no Lola-Verdict yet"
  sleep 20
done
echo MISSING > review-verdict.txt
echo "::error::Timed out waiting for Lola-Verdict: PASS|CHANGES on PR #$PR"
exit 1
